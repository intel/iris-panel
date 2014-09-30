from collections import defaultdict

from django import template

register = template.Library()


@register.filter
def group_and_sort_pbuilds(pbuilds):
    """
    Group PackageBuilds by package.name and order by status
    """
    groups = defaultdict(list)
    for pbuild in pbuilds:
        groups[pbuild.package.name].append(pbuild)
    def _sortkey(group):
        has_failure = len([i for i in group if i.status != 'SUCCESS'])
        key1 = '0' if has_failure else '1'
        return key1 + group[0].package.name
    return sorted(groups.values(), key=_sortkey)
