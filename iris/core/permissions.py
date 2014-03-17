# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This module contains user permission checkers.

Also offers custom permission methods for the
Django REST Framework API views; check documentation:
    http://www.django-rest-framework.org/api-guide/permissions
"""

from iris.core.models import Package, Product, GitTree, Domain
from iris.core.models import ProductRole, DomainRole, SubDomainRole, GitTreeRole


def can_edit(user, item):
    """
    Checks whether the user can edit the given item or not.

    Item is either a Package, Product, GitTree or Domain instance.

    User checking is done primarily is_superuser or is_staff methods.
    User checking is done secondarily on Role groups found in iris.core.groups.
    """

    if user.is_superuser or user.is_staff:
        return True

    pkg = item if isinstance(item, Package) else None
    product = item if isinstance(item, Product) else None
    tree = pkg.gittree if pkg else item if isinstance(item, GitTree) else None
    domain = tree if tree else item if isinstance(item, Domain) else None

    groups = []

    if product:
        groups = ProductRole.objects.filter(product=product)
    elif tree:
        groups = GitTreeRole.objects.filter(gittree=tree)
    elif domain:
        groups = DomainRole.objects.filter(domain=domain)

    for group in groups:
        if user in group.user_set.all() and (
                group.role == 'ARCHITECT' or group.role == 'MAINTAINER'):
            return True

def can_create(user, roles):
    """
    Returns True if user is staff or admin or has an ARCHITECT role.

    Roles is a queryset of role objects that have a role field.
    Role field is a CharField that can contain ARCHITECT.
    """

    if user.is_staff or user.is_superuser:
        return True

    for role in roles.filter(role='ARCHITECT'):
        if user in role.user_set.all():
            return True

def can_create_products(user):
    """
    Checks whether the user can create Products or not.
    """

    if user.has_perm('core.add_product'):
        return True

    return can_create(user, ProductRole.objects.all())

def can_create_domains(user):
    """
    Checks whether the user can create Domains or not.
    """

    if user.has_perm('core.add_domain'):
        return True

    return can_create(user, DomainRole.objects.all())

def can_create_subdomains(user):
    """
    Checks whether the user can create SubDomains or not.
    """

    if user.has_perm('core.add_subdomain'):
        return True

    return can_create(user, SubDomainRole.objects.all())

def can_create_gittrees(user):
    """
    Checks whether the user can create GitTrees or not.
    """

    if user.has_perm('core.add_gittree'):
        return True

    return can_create(user, GitTreeRole.objects.all())

def can_create_packages(user):
    """
    Checks whether the user can create Packages or not.
    """

    if user.has_perm('core.add_package'):
        return True

    return user.is_staff or user.is_superuser

def can_create_licenses(user):
    """
    Checks whether the user can create Licenses or not.
    """

    if user.has_perm('core.add_license'):
        return True

    return user.is_staff or user.is_superuser

def can_create_images(user):
    """
    Checks whether the user can create Images or not.
    """

    if user.has_perm('core.add_image'):
        return True

    return user.is_staff or user.is_superuser

