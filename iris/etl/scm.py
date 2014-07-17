# -*- encoding: utf-8 -*-
"""
Module for importing git scm data into IRIS.

Data is available from:
    https://review.tizen.org/gerrit/gitweb?p=scm/meta/git.git
"""
# pylint: disable=E0611,E1101,F0401,R0914,C0103,W0142
# E0611: No name 'manage' in module 'iris'
# E1101: Class 'Domain' has no 'objects' member
# F0401: Unable to import 'iris.core.models'
# C0321: More than one statement on a single line
# C0103: Invalid name "uc"
# W0142: Used * or ** magic
import os
from django.contrib.auth.models import User

from iris.core.models import (
    Domain, SubDomain, GitTree, License,
    DomainRole, SubDomainRole, GitTreeRole)
from iris.core.models.user import (
    parties as party_choices, roles as role_choices)

from iris.etl.parser import parse_blocks, UserCache
from iris.etl.loader import get_default_loader


MAPPING = {
    'A': 'ARCHITECT',
    'B': 'BRANCH',
    'C': 'COMMENTS',
    'D': 'DOMAIN',
    'I': 'INTEGRATOR',
    'L': 'LICENSES',
    'M': 'MAINTAINER',
    'N': 'PARENT',
    'O': 'DESCRIPTION',
    'R': 'REVIEWER',
    'T': 'TREE',
    'SL': 'SUBDOMAIN_LEADER',
}

ROLES = {i for i, _ in role_choices()}

NONAME = 'Uncategorized'


def parse_name(name):
    """parse domain name and subdomain name from the given name
    """
    parts = [i.strip() for i in name.split('/', 1)]
    if len(parts) == 1:
        if parts[0]:
            return parts[0], NONAME
        return NONAME, NONAME
    return parts


def build_user_cache(rawdata):
    """
    Go over all scm data to build a full UserCache
    """
    uc = UserCache()
    for typ, data in rawdata:
        for role in ROLES & set(data.keys()):
            for ustring in data[role]:
                uc.update(ustring)
    return uc


def rolename(role, name):
    """create role name
    """
    return '%s: %s' % (role, name)


def subrolename(role, dname, sname):
    """create subdomain role name
    """
    return '%s: %s-%s' % (role, dname, sname)


def transform_domains(rawdata, uc):
    """
    Transform to Domain, SubDomain,
    DomainRole, SubDomainRole,
    DomainRole.user_set and SubDomainRole.user_set
    """
    domains, subdomains = [{'name': NONAME}], []
    domainroles, subdomainroles = [], []
    domainrole_users, subdomainrole_users = [], []

    def _trans_subdomain(data):
        """transform subdomain item"""
        dname, sname = parse_name(data['DOMAIN'][0])
        subdomains.append({'name': sname, 'domain__name': dname})
        for role in ROLES & set(data.keys()):
            sr = {'role': role,
                  'subdomain__name': sname,
                  'subdomain__domain__name': dname}
            subdomainroles.append(
                dict(sr, name=subrolename(role, dname, sname)))
            for ustring in data[role]:
                user = uc.get(ustring)
                if user:
                    subdomainrole_users.append((sr, user))

    def _trans_domain(data):
        """transform domain item"""
        name = data['DOMAIN'][0]
        domains.append({'name': name})
        for role in ROLES & set(data.keys()):
            dr = {'role': role,
                  'domain__name': name}
            domainroles.append(dict(dr, name=rolename(role, name)))
            for ustring in data[role]:
                user = uc.get(ustring)
                if user:
                    domainrole_users.append((dr, user))

    for typ, data in rawdata:
        if typ != 'DOMAIN':
            continue
        elif 'PARENT' in data:
            # assume that a submain can't appear before its parent
            _trans_subdomain(data)
        else:
            _trans_domain(data)

    # Uncategorized Subdomain
    for domain in domains:
        subdomains.append({'name': NONAME, 'domain__name': domain['name']})
    return (domains, subdomains,
            domainroles, subdomainroles,
            domainrole_users, subdomainrole_users)


def transform_trees(rawdata, uc):
    """
    Transform to GitTree, GitTree.licenses
    GitTreeRole, GitTreeRole.user_set
    """
    trees, tree_licenses = [], []
    treeroles, treerole_users = [], []
    no_domain = ' / '.join([NONAME, NONAME])
    for typ, data in rawdata:
        if typ != 'TREE':
            continue
        path = data['TREE'][0]
        # if DOMAIN exists it must only have one value
        name = data.get('DOMAIN', [no_domain])[0] or no_domain
        if ' / ' not in name:
            name = ' / '.join([name, NONAME])
        dname, sname = name.split(' / ', 1)
        trees.append({'gitpath': path,
                      'subdomain__name': sname,
                      'subdomain__domain__name': dname})

        for licen in data.get('LICENSES', ()):
            tree_licenses.append(({'gitpath': path}, {'shortname': licen}))

        for role in ROLES & set(data.keys()):
            tr = {'role': role,
                  'gittree__gitpath': path}
            treeroles.append(dict(tr, name=rolename(role, path)))
            for ustring in data[role]:
                user = uc.get(ustring)
                if user:
                    treerole_users.append((tr, user))
    return (trees, tree_licenses,
            treeroles, treerole_users)


def transform_users(ucusers):
    """
    Transform cached users to database compatible users

    Field username is used for login and it's an unique field. The
    correct value of this field is stored in LDAP server, we can't
    get it here, so we use email as username when importing data.
    """
    return [dict(username=i['email'], **i) for i in ucusers]


def from_string(scm_str, coding='utf8'):
    """
    Import scm data from string.

    If input string is not unicode, try to decode them using `coding`
    """
    if isinstance(scm_str, str):
        scm_str = scm_str.decode(coding)
    return from_unicode(scm_str)


def from_unicode(scm_unicode):
    """
    Import scm data from unicode string.

    Strings return from Django model are all unicode. So it will be much
    easier to only deal with unicode string.
    """
    # 1.parse
    rawdata = parse_blocks(scm_unicode, MAPPING)

    # 2.extract and transform
    uc = build_user_cache(rawdata)
    users = transform_users(uc.all())

    (domains, subdomains,
     domainroles, subdomainroles,
     domainrole_users, subdomainrole_users,
     ) = transform_domains(rawdata, uc)

    (trees, tree_licenses,
     treeroles, treerole_users,
     ) = transform_trees(rawdata, uc)


    # 3.load
    loader = get_default_loader()
    loader.sync_entity(users, User)
    delete_domains = loader.sync_entity(domains, Domain)
    delete_subdomains = loader.sync_entity(subdomains, SubDomain)
    delete_domainroles = loader.sync_entity(domainroles, DomainRole)
    delete_subdomainroles = loader.sync_entity(subdomainroles, SubDomainRole)
    delete_trees = loader.sync_entity(trees, GitTree)
    delete_treeroles = loader.sync_entity(treeroles, GitTreeRole)

    loader.sync_nnr(domainrole_users, DomainRole, User)
    loader.sync_nnr(subdomainrole_users, SubDomainRole, User)
    loader.sync_nnr(tree_licenses, GitTree, License)
    loader.sync_nnr(treerole_users, GitTreeRole, User)

    delete_treeroles()
    delete_subdomainroles()
    delete_domainroles()
    delete_trees()
    delete_subdomains()
    delete_domains()


def from_file(dfile, tfile):
    """
    import scm data from file.
    `dfile` and `tfile` should be file objects not file names.
    """
    return from_string(''.join([dfile.read(),
                                os.linesep, os.linesep,
                                tfile.read()]))
