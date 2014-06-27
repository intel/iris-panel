from email.utils import parseaddr

from django.core.validators import validate_email, ValidationError


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
    st = 0
    item = None
    for line in content.splitlines():
        line = line.rstrip()
        if not line:
            continue

        mark, val = line.split(':', 1)
        mark, val = mark.strip(), val.strip()
        field = mapping.get(mark, mark)

        if st == 0:
            if mark not in starter:
                raise ValueError("Syntax error: unexpected {} "
                                 "outside of {}".format(mark, starter))
            st = 1
        if st == 1:
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
