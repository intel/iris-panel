"""
Module for checking git scm data.

DOMAINS:
    ERROR:
        1. Lack of Domain.
        2. Domain is not unique.
        3. SubDomain lack of parent.
        4. SubDomain and parent do not match.
        5. user lack of email info.
        6. user's email is invalid.
GIT-TREE:
    ERROR:
        1. lack of domain.
        2. domain is not unique.
        3. lack of tree path.
        4. tree path is not unique.
        5. user lack of email info.
        6. user's email is invalid.
"""
import logging

from iris.etl.scm import MAPPING
from iris.etl.scm import ROLES
from iris.etl.parser import parse_blocks, parse_user

# pylint: disable=C0103,W0603
# C0103: 30,0: Invalid name "logger"
# W0603: 39,4:error: Using the global statement

logger = logging.getLogger(__name__)

_error = 0

def error(*args, **kw):
    "increase error count and log message"
    global _error
    _error += 1
    return logger.error(*args, **kw)


def check_scm(domain_str, gittree_str):
    """
    check domain and gittree file.
    The return value: zero means everything is ok, non-zero means something
    is wrong, and the number is the error num in total.
    """
    global _error
    _error = 0
    domains_data = parse_blocks(domain_str, MAPPING)
    trees_data = parse_blocks(gittree_str, MAPPING)
    domains = check_domain(domains_data)
    check_gittree(trees_data, domains)
    return _error


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
    block_num = 0
    for _typ, block in domains_data:
        block_num += 1
        domain = block.get("DOMAIN")
        if domain is None:
            error("(DOMAINS): Lack of DOMAIN in block %s" % (block_num))
        elif len(domain) > 1:
            error("(DOMAINS): DOMAIN is not unique in block "
                  "%s %s" % (block_num, domain))

        name = domain[0]
        if name in names:
            error("(DOMAINS): Duplicated domain name: %s", name)
        names.add(name)

        if '/' in name:
            if "PARENT" not in block:
                error("(DOMAINS): SUBDOMAIN %s lack of parent "
                      "information", name)
            else:
                parent = name.split('/')[0].strip()
                if not parent == block.get("PARENT")[0].strip():
                    error('(DOMAINS): DOMAIN "%s" and Parent'
                          ' "%s" do not match'
                          % (domain[0], block.get("PARENT")[0]))

                if parent not in names:
                    error("(DOMAINS): Unknown parent domain name: %s", parent)

        for role, val in block.iteritems():
            if role in ROLES:
                for user in val:
                    check_user(user, "DOMAINS", block_num)
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
    block_num = 0
    pathes = set()

    for _typ, block in trees_data:
        block_num += 1
        domain = block.get("DOMAIN")
        if domain is None:
            error("(TREE): Lack of DOMAIN in block %s:%s"
                  % (block_num, block.get("TREE")))
        elif len(domain) > 1:
            error("(TREE): DOMAIN is not unique in block "
                  "%s %s" % (block_num, domain))
        domain = domain[0]
        if domain not in domains:
            error("(TREE): Unknown domain name: %s", domain)

        tree = block.get("TREE")
        if tree is None:
            error("(TREE): Lack of TREE PATH in block %s:%s"
                  % (block_num, block.get("DOMAIN")))
        elif len(tree) > 1:
            error("(TREE): TREE PATH is not unique in block "
                  "%s %s" % (block_num, tree))
        tree = tree[0]
        if tree in pathes:
            error("(TREE): Duplicate git path: %s", tree)

        for role, val in block.iteritems():
            if role in ROLES:
                for user in val:
                    check_user(user, "TREE", block_num)


def check_user(ustring, data_typ, block_num):
    """
    Check user string is valid or not.
    ERROR: The email of user is blank or invalid.
    """
    try:
        parse_user(ustring, True)
    except ValueError as err:
        error("(%s): %s in block %s", data_typ, err, block_num)
        return 1
    return 0
