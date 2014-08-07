"""
Module for checking git scm data.
"""
import logging

from iris.etl.scm import MAPPING
from iris.etl.scm import ROLES
from iris.etl.parser import parse_blocks, parse_user

# pylint: disable=C0103,W0603
# C0103: 30,0: Invalid name "logger"
# W0603: 39,4:error: Using the global statement

logger = logging.getLogger(__name__)

_message = []


def error(*args, **kw):
    "increase error count and log message"
    global _message
    _message.append(*args)
    return logger.error(*args, **kw)


def check_scm(domain_str, gittree_str):
    """
    check domain and gittree file.
    The return value: zero means everything is ok, non-zero means something
    is wrong, and the number is the error num in total.
    """
    global _error, _message
    _message = []
    domains_data = parse_blocks(domain_str, MAPPING)
    trees_data = parse_blocks(gittree_str, MAPPING)
    domains = check_domain(domains_data)
    check_gittree(trees_data, domains)
    return {'errors': len(_message), 'messages': _message}


def check_domain(domains_data):
    """
    Check the content of domain file is valid or not for the following errors:

    * Lack of Domain.
    * Domain is not unique.
    * Subdomain lack of parent.
    * Domain and Parent do not match.
    * Duplicated domain or subdomain name
    * Unknown parent domain name
    """
    names = set()
    for block_num, (_typ, block) in enumerate(domains_data):
        domain = block.get("DOMAIN")
        if domain is None:
            error("(DOMAINS): Lack of DOMAIN in block %s" % block_num)
            continue
        elif len(domain) > 1:
            error("(DOMAINS): Multi domain names: %s" % domain)
            continue

        domain = domain[0]
        if domain in names:
            error("(DOMAINS): Duplicated domain name: %s" % domain)
            continue
        names.add(domain)

        if '/' in domain:
            if "PARENT" not in block:
                error("(DOMAINS): Lack of parent for domain %s" % domain)
                continue
            else:
                parent = block.get("PARENT")[0].strip()
                domainname = domain.split('/')[0].strip()
                if parent != domainname:
                    error('(DOMAINS): DOMAIN "%s" and Parent "%s" do not match'
                          % (domainname, parent))
                    continue
                if parent not in names:
                    error("(DOMAINS): Unknown parent domain name: %s" % parent)
                    continue

        for role, val in block.items():
            if role in ROLES:
                for user in val:
                    check_user(user, "DOMAINS")
    return names


def check_gittree(trees_data, domains):
    """
    Check the content of git-tree file is valid or not for the following errors:

    * Lack of Domain.
    * Domain is not unique.
    * Lack of Tree Path.
    * Tree Path is not unique.
    * Duplicated git path
    * Unknown domain name
    """
    pathes = set()

    for block_num, (_typ, block) in enumerate(trees_data):
        tree = block.get("TREE")
        if tree is None:
            error("(TREE): Lack of TREE PATH in block %s" % block_num)
            continue
        elif len(tree) > 1:
            error("(TREE): Multi tree pathes: %s" % tree)
            continue
        tree = tree[0]
        if tree in pathes:
            error("(TREE): Duplicated git path: %s" % tree)
            continue

        domain = block.get("DOMAIN")
        if domain is None:
            error("(TREE): Lack of DOMAIN for git tree %s" % tree)
            continue
        elif len(domain) > 1:
            error("(TREE): Multi DOMAIN for git tree %s" % tree)
            continue
        domain = domain[0]
        if domain not in domains:
            error("(TREE): Unknown domain name: %s" % domain)
            continue

        for role, val in block.iteritems():
            if role in ROLES:
                for user in val:
                    check_user(user, "TREE")


def check_user(ustring, data_typ):
    """
    Check user string is valid or not.
    ERROR: The email of user is blank or invalid.
    """
    try:
        parse_user(ustring, True)
    except ValueError as err:
        error("(%s): %s" % (data_typ, err))
        return 1
    return 0
