# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This module contains user injectors.

Injectors are to be used to augment the standard User model
and add role resolving methods to it when needed.

When we need to e.g. list all parties or specific roles
for an user we can inject as the example below shows.
"""

# pylint: disable=C0111


def inject_user_getters(user):
    """
    Injects the following methods into the given user object:
        * get_user_parties
        * get_domain_roles
        * get_gittree_roles
        * get_product_roles

    :param  user:           User to inject methods into
    :type   type:           Django User class instance

    Example usage::

        >>> from django.contrib.auth.models import User
        >>> from iris.core import injectors
        >>> user = User.objects.get(username='Foomaster')
        >>> inject_user_getters(user).get_user_parties()
        [<Group: Intel>, <Group: Tizen.org>]
    """
    groups = user.groups.select_related(
        'userparty',
        'domainrole', 'domainrole__domain',
        'subdomainrole', 'subdomainrole__subdomain',
        'gittreerole', 'gittreerole__gittree',
        ).all()

    def get_userparties():
        return [up.userparty for up in groups
                if hasattr(up, 'userparty')]

    def get_domainroles():
        return [dr.domainrole for dr in groups
                if hasattr(dr, 'domainrole')]

    def get_subdomainroles():
        return [sdr.subdomainrole for sdr in groups
                if hasattr(sdr, 'subdomainrole')]

    def get_gittreeroles():
        return [gr.gittreerole for gr in groups
                if hasattr(gr, 'gittreerole')]

    (user.get_userparties, user.get_domainroles,
     user.get_subdomainroles, user.get_gittreeroles) = (
        get_userparties, get_domainroles,
        get_subdomainroles, get_gittreeroles)

    return user
