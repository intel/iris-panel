"""
Parsing code for scm text
"""
import re
import os
import glob
import gzip

from email.utils import parseaddr
from xml.dom import minidom

from django.core.validators import validate_email, ValidationError


ADDRESS = re.compile(r'((.*?)<(.*?)>)|(.*@.*)')


class UserCache(object):
    """Cache user string to merge duplication"""
    def __init__(self):
        self.groups = []
        self.index = {}

    def update(self, ustring):
        """Update user string into cache"""
        def _eq(user1, user2):
            """
            True if two users are equal.

            If they both have email, then compare emails;
            Else if they have name, then compare names.
            """
            email1, first1, last1 = user1
            email2, first2, last2 = user2
            return (email1 and email1 == email2) or \
                (first1 or last1) and (first1, last1) == (first2, last2)

        def _is_group_match(group, name):
            """is there any user equals in a group"""
            return any((_eq(name, i) for i in group))

        name = parse_user(ustring)
        newg = set()
        ngs = []
        for group in self.groups:
            if _is_group_match(group, name):
                newg |= group
            else:
                ngs.append(group)
        newg.add(name)
        ngs.append(newg)
        self.groups = ngs

        user = self._make_user(newg)
        for name in newg:
            self.index[name] = user

    @staticmethod
    def is_user_valid(user):
        """Only consider users with email"""
        return 'email' in user and user['email']

    def all(self):
        """Returns all users"""
        return [j for j in
                [self._make_user(i) for i in self.groups]
                if self.is_user_valid(j)]

    def get(self, ustring):
        """Get a user by a given user string"""
        user = self.index.get(parse_user(ustring))
        if self.is_user_valid(user):
            return user

    @staticmethod
    def _make_user(group):
        """Make full user fields from cache"""
        keys = ('email', 'first_name', 'last_name')
        user = dict(zip(keys, ('', '', '')))
        for i in group:
            user.update({k: v for k, v in zip(keys, i) if v})
        return user


def parse_user(ustring, validate=False):
    """
    Parse user string like To or Cc field.

    >>> parse_user('Jim Morrison <jim.morrison@doors.com>')
    ('jim.morrison@doors.com', 'Jim', 'Morrison')
    """
    result = ADDRESS.match(ustring)
    if not result:
        user = ustring
        email = ''
    elif result.group(1):
        user = result.group(2)
        email = result.group(3)
    else:
        user = ''
        email = ustring
    user, email = user.strip(), email.strip()

    if validate and email:
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError('Invalid email "%s" for user "%s"' % (
                    email, ustring))

    first, last = '', ''
    parts = user.split(None, 1)
    if len(parts) == 2:
        first, last = parts
    elif len(parts) == 1:
        first = parts[0]

    return email, first, last


def parse_blocks(content, mapping=()):
    """
    Parse blocks of scm/meta/git info into a list of py dicts.

    >>> parse_blocks('''
    ... D: SCM
    ... M: Alice@i.com
    ...
    ... D: SCM / BB
    ... N: SCM
    ... R: Michael
    ...
    ... T: scm/meta/git
    ... D: SCM / BB
    ... M: Bob@a.com
    ... ''', {'D':'Domain', 'T': 'Tree', 'M':'Maintainer',
    ...       'N':'Parent', 'R':'Reviewer'})
    [('Domain', {'Domain': ['SCM'], 'Maintainer': ['Alice@i.com']}), \
('Domain', {'Reviewer': ['Michael'], 'Domain': ['SCM / BB'], \
'Parent': ['SCM']}), \
('Tree', {'Maintainer': ['Bob@a.com'], 'Domain': ['SCM / BB'], \
'Tree': ['scm/meta/git']})]
    """
    if not content.strip():
        raise ValueError("Content must be not empty")
    # add \n\n at the end to close the last block which simplify parsing code
    content = ''.join([content, os.linesep, os.linesep])
    mapping = dict(mapping or ())

    def parse_kv(line):
        try:
            mark, val = line.split(':', 1)
        except ValueError:
            raise ValueError("Can't find colon(:) at line: %s" % line)
        mark, val = mark.strip(), val.strip()
        field = mapping.get(mark, mark)
        return field, val

    res = []
    state = 0
    typ, item = None, None
    for line in content.splitlines():
        line = line.rstrip()
        if state == 0 and line:
            state = 1
            field, val = parse_kv(line)
            typ = field
            item = {field: [val]}
        elif state == 1 and line:
            field, val = parse_kv(line)
            if field in item:
                item[field].append(val)
            else:
                item[field] = [val]
        elif state == 1 and not line:
            state = 0
            res.append((typ, item))
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
