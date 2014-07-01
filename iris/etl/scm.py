# -*- encoding: utf-8 -*-
"""
Module for importing git scm data into IRIS.

Data is available from:
    https://review.tizen.org/gerrit/gitweb?p=scm/meta/git.git
"""
# pylint: disable=E0611,E1101,F0401,R0914
#E0611: No name 'manage' in module 'iris'
#E1101: Class 'Domain' has no 'objects' member
#F0401: Unable to import 'iris.core.models'
#C0321: More than one statement on a single line

from django.contrib.auth.models import User

from iris.core.models import (
    Domain, SubDomain, GitTree, DomainRole, License,
    SubDomainRole, GitTreeRole, UserParty)
from iris.etl.parser import parse_blocks, parse_user


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
    'T': 'TREE PATH',
    'SL': 'SUBDOMAIN_LEADER',
}

ROLES = ['ARCHITECT', 'INTEGRATOR', 'MAINTAINER', 'REVIEWER']

NONAME = 'Uncategorized'


def parse_name(name):
    """parse domain name and subdomain name from the given name
    """
    names = name.split(' / ', 1)
    domain = names[0]
    subdomain = names[1] if len(names) > 1 else 'Uncategorized'

    return domain, subdomain


def diff(new, old, key=None):
    """get intersection and difference of two lists
    """
    if key:
        newidx = {key(i):i for i in new}
        oldidx = {key(i):i for i in old}
        news = set(newidx.keys())
        olds = set(oldidx.keys())
    else:
        news = set(new)
        olds = set(old)

    added = news.difference(olds)
    thesame = news.intersection(olds)
    deleted = olds.difference(news)

    if key:
        added = [newidx[i] for i in added]
        for i in thesame: #HACK
            if type(newidx[i]) is not tuple:
                newidx[i].id = oldidx[i].id
        thesame = [newidx[i] for i in thesame]
        deleted = [oldidx[i] for i in deleted]
    else:
        added = list(added)
        thesame = list(thesame)
        deleted = list(deleted)

    return added, thesame, deleted


def transform(domains_data, trees_data):
    """transform data
    """
    users = {}
    party = [('Intel', 'INTEL'), ('Samsung', 'SAMSUNG'), ('Tizen OSS', 'TIZEN')]
    party_roles = [UserParty(name=pn, party=p) for pn, p in party]
    user_party_roles = []

    def update_user(addr):
        """update user information
        """
        email, first, last = parse_user(addr)
        if not email:
            return

        if email in users:
            user = users[email]
            user.first_name = user.first_name or first
            user.last_name = user.last_name or last
        else:
            user = User(username=email, first_name=first, last_name=last,
                email=email)
            users[email] = user

        if '@intel.com' in email:
            (party_name, party) = ('Intel', 'INTEL')
        elif '@samsung.com' in email:
            (party_name, party) = ('Samsung', 'SAMSUNG')
        else:
            (party_name, party) = ('Tizen OSS', 'TIZEN')

        user_party_roles.append((UserParty(name=party_name, party=party), user))
        return user

    # Domain, Subdomain, User, DomainRole, SubDomainRole
    domains = {NONAME: Domain(name=NONAME)}
    subdomains = {}
    domain_roles = {}
    subdomain_roles = {}

    def rolename(role, name):
        """create role name
        """
        return '%s: %s' % (role, name)

    def subrolename(role, dname, sname):
        """create subdomain role name
        """
        return '%s: %s-%s' % (role, dname, sname)

    for data in domains_data:
        name = data['DOMAIN']
        if 'PARENT' in data:
            dname, sname = parse_name(name)
            # assume that a submain can't appear before its parent
            subdomain = SubDomain(name=sname, domain=domains[dname])
            subdomains[name] = subdomain
            subdomain_roles.update({rolename(role, name):
                SubDomainRole(name=subrolename(role, dname, sname), role=role,
                subdomain=subdomain)for role in ROLES if role in data})
        else:
            domain = Domain(name=name)
            domains[name] = domain
            domain_roles.update({rolename(role, name):
                DomainRole(name=rolename(role, name), role=role, domain=domain
                )for role in ROLES if role in data})

        # User
        for role in ROLES:
            if role in data:
                for i, addr in enumerate(data[role]):
                    data[role][i] = update_user(addr)

    # Uncategorized Subdomain
    for dname, domain in domains.items(): # will be removed in future
        sname = NONAME
        name = ' / '.join([dname, sname])
        subdomain = SubDomain(name=sname, domain=domain)
        subdomains[name] = subdomain

    # Gittree, User
    trees = []
    trees_licenses = []
    tree_roles = []
    user_gittreerole = []
    for data in trees_data:
        path = data['TREE PATH']
        # DOMAIN key exists or not, if exists, its values has only one item
        name = data.get('DOMAIN', [NONAME])[0] or NONAME
        if ' / ' not in name: # will be removed in future
            name = ' / '.join([name, NONAME])
        tree = GitTree(gitpath=path, subdomain=subdomains[name])
        trees.append(tree)
        for licen in data.get('LICENSES', ()):
            license_obj = License.objects.get(shortname=licen)
            trees_licenses.append((tree, license_obj))

        for role in ROLES:
            if role in data:
                tree_role = GitTreeRole(name=rolename(role, path), gittree=tree,
                    role=role)
                tree_roles.append(tree_role)
                for i, addr in enumerate(data[role]):
                    _user = update_user(addr)
                    if _user:
                        data[role][i] = _user
                        user_gittreerole.append((tree_role, _user))

    # User-Group
    # user-domainrole
    user_domainrole = []
    user_subdomainrole = []
    for data in domains_data:
        name = data['DOMAIN']
        if 'PARENT' not in data:
            for role in ROLES:
                if role in data:
                    domain_role = domain_roles[rolename(role, name)]
                    user_domainrole.extend([(domain_role, i)
                        for i in data[role] if i])
        else:
            for role in ROLES:
                if role in data:
                    subdomain_role = subdomain_roles[rolename(role, name)]
                    user_subdomainrole.extend((subdomain_role, i)
                        for i in data[role] if i)

    return (domains.values(), subdomains.values(), trees, trees_licenses,
            domain_roles.values(), subdomain_roles.values(), users.values(),
            tree_roles, user_domainrole, user_subdomainrole,
            user_gittreerole, party_roles, user_party_roles
            )


def load_entity(new, old, key, delete=True, update_fields=None):
    """load entity into database
    """
    added, thesame, deleted = diff(new, old, key)
    if new:
        print '{:>15}: added={:<5} thesame={:<5} deleted={:<5} {:<5}'.format(
        new[0].__class__.__name__, len(added), len(thesame),
        len(deleted), delete)
    for i in added:
        i.save()
    if delete:
        for i in deleted:
            i.delete()
    if update_fields:
        for i in thesame:
            i.save(update_fields=update_fields)


def load_relation(new, old, key):
    """load relation into database
    """
    added, thesame, deleted = diff(new, old, key)
    if new:
        print '{:>15} users: added={:<5} thesame={:<5} deleted={:<5}'.format(
        new[0][0].__class__.__name__, len(added), len(thesame), len(deleted))
    for role, user in added:
        role.__class__.objects.get(name=role.name).user_set.add(
            User.objects.get(username=user.email))
    for role, user in deleted:
        role.__class__.objects.get(name=role.name).user_set.remove(user)

def load_license(new, old, key):
    """load license into database
    """
    added, thesame, deleted = diff(new, old, key)
    if new:
        print '{:>15} license: added={:<5} thesame={:<5} deleted={:<5}'.format(
        new[0][0].__class__.__name__, len(added), len(thesame), len(deleted))
    for tree, licen in added:
        tree.licenses.add(licen)
    for tree, licen in deleted:
        tree.licenses.remove(licen)

def incremental_import_core(domain_str, gittree_str):
    """import data
    """
    domains_data = parse_blocks(domain_str, 'D', MAPPING)
    trees_data = parse_blocks(gittree_str, 'T', MAPPING)

    (domains, subdomains, trees, trees_licenses,
     domain_roles, subdomain_roles, users,
     tree_roles, user_domainrole, user_subdomainrole,
     user_treerole, party_roles, user_party_roles,
     ) = transform(domains_data, trees_data)

    load_entity(domains, Domain.objects.all(), lambda i: i.name)
    #HACK
    for i in subdomains:
        i.domain = i.domain
    for i in domain_roles:
        i.domain = i.domain

    load_entity(subdomains, SubDomain.objects.select_related('domain').all(),
        lambda i: '/'.join([i.name, i.domain.name]))
    for i in trees:
        i.subdomain = i.subdomain
    for i in subdomain_roles:
        i.subdomain = i.subdomain

    load_entity(trees, GitTree.objects.select_related('subdomain',
        'subdomain__domain').all(), lambda i: i.gitpath,
        update_fields=['subdomain'])

    load_entity(domain_roles, DomainRole.objects.select_related('domain'),
        lambda i: '%s: %s' % (i.role, i.domain.name), delete=True)

    load_entity(subdomain_roles, SubDomainRole.objects.select_related(
        'subdomain', 'subdomain__domain'), lambda i: '%s: %s / %s' % (i.role,
        i.subdomain.domain.name, i.subdomain.name), delete=True)

    for i in tree_roles:
        i.gittree = i.gittree
    load_entity(tree_roles, GitTreeRole.objects.select_related('gittree',
        'gittree__subdomain'), lambda i: '%s: %s' % (i.role, i.gittree.gitpath),
        delete=True)

    load_entity(users, User.objects.all(),
        lambda i: i.email, delete=False,
        update_fields=['first_name', 'last_name'])

    # HACK
    db_user_domainrole = [(g, u)
        for g in DomainRole.objects.select_related('domain').all().
        prefetch_related('user_set') for u in g.user_set.all()
        ]
    load_relation(user_domainrole, db_user_domainrole,
        lambda (g, u): '%s: %s - %s' % (g.role, g.domain.name, u.email))

    db_user_subdomainrole = [(g, u)
        for g in SubDomainRole.objects.select_related('subdomain').all().
        prefetch_related('user_set') for u in g.user_set.all()
        ]
    load_relation(user_subdomainrole, db_user_subdomainrole,
        lambda (g, u): '%s: %s - %s' % (g.role, g.subdomain.name, u.email))

    db_user_treerole = [(g, u)
        for g in GitTreeRole.objects.select_related('gittree').all().
        prefetch_related('user_set') for u in g.user_set.all()
        ]
    load_relation(user_treerole, db_user_treerole,
        lambda (g, u): '%s: %s - %s' % (g.role, g.gittree.gitpath, u.email))

    load_entity(party_roles, UserParty.objects.all(), lambda i: i.name)

    db_user_partyrole = [(g, u)
        for g in UserParty.objects.select_related('user').all().
        prefetch_related('user_set') for u in g.user_set.all()
        ]
    load_relation(user_party_roles, db_user_partyrole,
        lambda (g, u): '%s: %s' % (g.party, u.email))

    db_gitree_licenses = [(t, l) for t in GitTree.objects.all().
        prefetch_related('licenses') for l in t.licenses.all()]
    load_license(trees_licenses, db_gitree_licenses,
        lambda (t, l): '%s: %s' %(t.gitpath, l.shortname))

def incremental_import(domain_file, gittree_file):
    incremental_import_core(domain_file.read(), gittree_file.read())
