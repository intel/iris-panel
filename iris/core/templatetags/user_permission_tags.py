# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the Django template tag file for the IRIS project.
"""

# pylint: disable=C0103

from django import template
from iris.core.permissions import (can_edit, can_create_products,
        can_create_domains, can_create_subdomains, can_create_gittrees,
        can_create_packages, can_create_licenses, can_create_images)

register = template.Library()

@register.assignment_tag(name='check_user_permissions_for')
def check_user_permissions_for(user, item):
    """
    Checks user permissions for editing items in templates.

    Refer to implementation in iris.core.permissions.
    """

    return can_edit(user, item)

@register.assignment_tag(name='check_can_create_products')
def can_create_products_proxy(user):
    """
    Proxies permission checks for creating products to templates.
    """

    return can_create_products(user)

@register.assignment_tag(name='check_can_create_domains')
def can_create_domains_proxy(user):
    """
    Proxies permission checks for creating domains to templates.
    """

    return can_create_domains(user)

@register.assignment_tag(name='check_can_create_subdomains')
def can_create_subdomains_proxy(user):
    """
    Proxies permission checks for creating subdomains to templates.
    """

    return can_create_subdomains(user)


@register.assignment_tag(name='check_can_create_gittrees')
def can_create_gittrees_proxy(user):
    """
    Proxies permission checks for creating gittrees to templates.
    """

    return can_create_gittrees(user)

@register.assignment_tag(name='check_can_create_packages')
def can_create_packages_proxy(user):
    """
    Proxies permission checks for creating packages to templates.
    """

    return can_create_packages(user)

@register.assignment_tag(name='check_can_create_licenses')
def can_create_licenses_proxy(user):
    """
    Proxies permission checks for creating licenses to templates.
    """

    return can_create_licenses(user)

@register.assignment_tag(name='check_can_create_images')
def can_create_images_proxy(user):
    """
    Proxies permission checks for creating images to templates.
    """

    return can_create_images(user)
