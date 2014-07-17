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
from email.utils import parseaddr

from django.core.validators import ValidationError

from iris.etl.scm import MAPPING
from iris.etl.scm import ROLES
from iris.etl.parser import parse_blocks, parse_user

logger = logging.getLogger(__name__)


def check_scm(domain_str, gittree_str):
    """
    check domain and gittree file.
    The return value: zero means everything is ok, non-zero means something
    is wrong, and the number is the error num in total.
    """
    domains_data = parse_blocks(domain_str, MAPPING)
    trees_data = parse_blocks(gittree_str, MAPPING)
    err_in_domain = check_domain(domains_data)
    err_in_gittree = check_gittree(trees_data)
    return err_in_domain + err_in_gittree


def check_domain(domains_data):
    """
    check the content of domain file is valid or not.
    ERROR1: Lack of Domain.
    ERROR2: Domain is not unique.
    ERROR3: Subdomain lack of parent.
    ERROR4: Domain and Parent do not match.
    """
    err_num = 0
    block_num = 0
    for typ, block in domains_data:
        block_num += 1
        domain = block.get("DOMAIN")
        if domain is None:
            logger.error("(DOMAINS): Lack of DOMAIN in block %s" % (block_num))
            err_num += 1
        elif len(domain) > 1:
            logger.error("(DOMAINS): DOMAIN is not unique in block "
                         "%s %s" % (block_num, domain))
            err_num += 1
        elif "/" in domain[0]:
            if "PARENT" not in block.keys():
                logger.error("(DOMAINS): SUBDOMAIN %s lack of parent"
                             " information" % (domain[0]))
                err_num += 1
            else:
                parent = domain[0].split('/')[0].strip()
                if not parent == block.get("PARENT")[0].strip():
                    logger.error("(DOMAINS): DOMAIN \"%s\" and Parent"
                                 " \"%s\" do not match"
                                 % (domain[0], block.get("PARENT")[0]))
                    err_num += 1
        for role, val in block.iteritems():
            if role in ROLES:
                for user in val:
                    err_num = err_num + check_user(user, "DOMAINS", block_num)
    return err_num


def check_gittree(trees_data):
    """
    Check the content of git-tree file is valid or not.
    ERROR1: Lack of Domain.
    ERROR2: Domain is not unique.
    ERROR3: Lack of Tree Path.
    ERROR4: Tree Path is not unique.
    """
    block_num = 0
    err_num = 0

    for typ, block in trees_data:
        block_num += 1
        domain = block.get("DOMAIN")
        if domain is None:
            logger.error("(TREE): Lack of DOMAIN in block %s:%s"
                         % (block_num, block.get("TREE")))
            err_num += 1
        elif len(domain) > 1:
            logger.error("(TREE): DOMAIN is not unique in block "
                         "%s %s" % (block_num, domain))
            err_num += 1
        tree = block.get("TREE")
        if tree is None:
            logger.error("(TREE): Lack of TREE PATH in block %s:%s"
                         % (block_num, block.get("DOMAIN")))
            err_num += 1
        elif len(tree) > 1:
            logger.error("(TREE): TREE PATH is not unique in block "
                         "%s %s" % (block_num, tree))
            err_num += 1
        for role, val in block.iteritems():
            if role in ROLES:
                for user in val:
                    err_num = err_num + check_user(user, "TREE", block_num)
    return err_num


def check_user(ustring, data_typ, block_num):
    """
    Check user string is valid or not.
    ERROR: The email of user is blank or invalid.
    """
    try:
        parse_user(ustring, True)
    except ValueError as err:
        logger.error("(%s): %s in block %s", data_typ, err, block_num)
        return 1
    return 0
