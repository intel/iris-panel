# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
from django import template

register = template.Library()


@register.filter
def user_display_name(user):
    names = []
    if user.last_name:
        names.append(user.last_name)
    if user.first_name:
        names.append(user.first_name)
    if names:
        return ', '.join(names)
    return user.username.split('@', 1)[0]
