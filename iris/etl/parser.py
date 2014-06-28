# -*- encoding: utf-8 -*-
"""
Parsing code for scm text
"""
import os
import glob
import gzip

from email.utils import parseaddr
from xml.dom import minidom

from django.core.validators import validate_email, ValidationError


class UserCache(object):
    """Cache user string to merge duplication"""
    def __init__(self):
        self.groups = []
        self.index = {}

    def update(self, ustring):
        """Update user string into cache"""
        def _eq(user1, user2):
            "compare two users"
            email1, first1, last1 = user1
            email2, first2, last2 = user2
            return email1 == email2 or (first1, last1) == (first2, last2)

        def _is_group_match(group, name):
            "is there any user equals in a group"
            for i, _ in group:
                if _eq(name, i):
                    return True

        name = parse_user(ustring)
        newg = set()
        ngs = []
        for group in self.groups:
            if _is_group_match(group, name):
                newg |= group
            else:
                ngs.append(group)
        newg.add((name, ustring))
        ngs.append(newg)
        self.groups = ngs

        user = self._make_user(newg)
        for _, ustring in newg:
            self.index[ustring] = user

    def all(self):
        """Returns all users"""
        return [self._make_user(i) for i in self.groups]

    def get(self, ustring):
        """Get a user by a given user string"""
        return self.index.get(ustring)

    @staticmethod
    def _make_user(group):
        """Make full user fields from cache"""
        keys = ('email', 'first_name', 'last_name')
        user = dict(zip(keys, ('', '', '')))
        for i, _ in group:
            user.update({k: v for k, v in zip(keys, i) if v})
        return user


def parse_user(ustring):
    """
    Parse user string like To or Cc field.

    >>> parse_user('Jim Morrison <jim.morrison@doors.com>')
    ('jim.morrison@doors.com', 'Jim', 'Morrison')
    """
    user, email = parseaddr(ustring)
    if not user and '@' not in email:
        user, email = ustring, ''
    else:
        user, email = user.strip(), email.strip()
        try:
            validate_email(email)
        except ValidationError:
            email = ''

    first, last = '', ''
    parts = user.split(None, 1)
    if len(parts) == 2:
        first, last = parts
    elif len(parts) == 1:
        first = parts[0]

    return email, first, last


def parse_blocks(content, starter, mapping=()):
    """
    Parse blocks of scm/meta/git info into a list of py dicts.

    >>> parse_blocks('''
    ... D: SCM
    ... M: Alice@i.com
    ...
    ... D: SCM / BB
    ... N: SCM
    ... R: Michael@i.com
    ... ''', 'D', {'D':'Domain', 'M':'Maintainer',
    ...            'N':'Parent', 'R':'Reviewer'})
    [{'Domain': 'SCM', 'Maintainer': ['Alice@i.com']}, \
{'Reviewer': ['Michael@i.com'], 'Domain': 'SCM / BB', 'Parent': ['SCM']}]
    """
    mapping = dict(mapping)

    res = []
    state = 0
    item = None
    for line in content.splitlines():
        line = line.rstrip()
        if not line:
            continue

        mark, val = line.split(':', 1)
        mark, val = mark.strip(), val.strip()
        field = mapping.get(mark, mark)

        if state == 0:
            if mark not in starter:
                raise ValueError("Syntax error: unexpected {} "
                                 "outside of {}".format(mark, starter))
            state = 1
        if state == 1:
            if mark == starter:
                if item:
                    res.append(item)
                item = {field: val}
            elif field in item:
                item[field].append(val)
            else:
                item[field] = [val]

    if item:
        res.append(item)
    return res


def parse_xml(file_path, node):
    """parse xml file into a list of Element instances.
    """
    xmldoc = minidom.parse(file_path)
    itemlist = xmldoc.getElementsByTagName(node)

    return itemlist


def parse_str_xml(xml_str, node):
    """parse xml string into a list of Element instances.
    """
    xmldoc = minidom.parseString(xml_str)
    itemlist = xmldoc.getElementsByTagName(node)

    return itemlist


def parse_buildxml(file_path):
    """get build tatgets of xml items.
    """
    targets = []

    for item in parse_xml(file_path, 'buildtarget'):
        targets.append(item.attributes['name'].value)

    return targets


def parse_packages(file_path):
    """parse packages from xml.
    """
    packages = []

    for pkg_file in glob.glob(os.path.join(file_path, '*-primary.xml.gz')):
        with gzip.open(pkg_file) as pdata:
            content = pdata.read()
        for item in parse_str_xml(content, 'package'):
            pkg = item.getElementsByTagName('name')[0].firstChild.data
            tree = item.getElementsByTagName('version')[0]. \
                attributes['vcs'].value.split('#')[0]
            packages.append((pkg, tree))

    return packages


def parse_images(file_path, target):
    """parse images from xml.
    """
    images = []

    if not os.path.isfile(file_path):
        return images

    for item in parse_xml(file_path, 'config'):
        name = item.getElementsByTagName('name')[0].firstChild.data. \
            split('.')[0]
        arch = item.getElementsByTagName('arch')[0].firstChild.data
        images.append((target, arch, name))

    return images


def parse_trees_of_prod(tree_dir):
    """get trees of products from xml.
    """
    trees = []

    files = os.listdir(tree_dir)

    for t_file in files:
        file_path = os.path.join(tree_dir, t_file)
        for item in parse_xml(file_path, 'project'):
            tree = item.attributes['path'].value
            trees.append(tree)

    return list(set(trees))
