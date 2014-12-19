# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
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
