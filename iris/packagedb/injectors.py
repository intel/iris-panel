# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This module contains helpers such as property injectors for models.
"""

# pylint: disable=C0111

from iris.core.models import Domain, SubDomain, Package
from iris.core.models import DomainRole, SubDomainRole, GitTreeRole, ProductRole


def inject_base_getters(obj, user_resolver):
    """
    Injects the following functions into the object:
        * get_architects
        * get_maintainers
        * get_developers
        * get_reviewers
        * get_integrators


    :param  obj:            Django model object to inject into
    :type   obj:            Django model object
    :param  user_resolver:  Resolver for a list of user objects
    :type   user_resolver:  Function object

    Requires object to inject into and a method for resolving
    user list generating function such as the following example::

        def _get_users(role):
            queryset_list = DomainRole.objects.filter(role=role, domain=domain)
            return [user for users in queryset_list.user_set for user in users]

        inject_base_getters(obj, _get_users)

    Look for an example of the actual usage below.
    """

    def get_architects():
        return user_resolver('ARCHITECT')

    def get_maintainers():
        return user_resolver('MAINTAINER')

    def get_developers():
        return user_resolver('DEVELOPER')

    def get_reviewers():
        return user_resolver('REVIEWER')

    def get_integrators():
        return user_resolver('INTEGRATOR')

    (obj.get_architects, obj.get_maintainers, obj.get_developers,
        obj.get_reviewers, obj.get_integrators) = \
    (get_architects, get_maintainers, get_developers,
        get_reviewers, get_integrators)

    return obj

def inject_domain(domain):
    """
    An injector for setting Domain object's user getter methods for templates.
    These are split into a separate injectors to avoid bloating
    Django ORM objects by moving rendering related functionality
    out of the model classes to be added when needed.

    :param  domain:     Domain to inject the getter methods into
    :type   domain:     Domain model object

    Example usage::

        domains = [inject_subdomain(d) for d in Domain.objects.all()]
    """

    def _get_users(role):
        """
        Returns a list of users with given role for the Domain object.

        Queries for matching roles, which returns a queryset of groups.
        Constructs a list of users in queryset's role groups in-place
        """

        roles = DomainRole.objects.filter(role=role, domain=domain)
        return [user for group in roles for user in group.user_set.all()]

    def _get_subdomains():
        """
        Returns SubDomains belonging to this Domain object.

        Follows a backward relation from SubDomain model's domain
        field into the Domain object the subdomain belongs to, then
        back to the Domain the SubDomain belongs to.
        """

        return SubDomain.objects.filter(domain=domain)

    domain.get_subdomains = _get_subdomains
    return inject_base_getters(domain, _get_users)

def inject_subdomain(subdomain):
    """
    An injector for setting SubDomain object's getter methods for templates.
    These are split into a separate injectors to avoid bloating
    Django ORM objects by moving rendering related functionality
    out of the model classes to be added when needed.

    :param  subdomain:     SubDomain to inject the getter methods into
    :type   subdomain:     SubDomain model object

    Example usage::

        subdomains = [inject_subdomain(d) for d in SubDomain.objects.all()]
    """

    def _get_users(role):
        """
        Returns a list of users with given role for the SubDomain object.

        Queries for matching roles, which returns a queryset of groups.
        Constructs a list of users in queryset's role groups in-place
        """

        roles = SubDomainRole.objects.filter(role=role, subdomain=subdomain)
        return [user for group in roles for user in group.user_set.all()]

    def _get_packages():
        """
        Returns Packages belonging to this SubDomain object.

        Follows a backward relation from Package model's gittree
        field into the GitTree object the package belongs to, then
        back to the SubDomain the GitTree belongs to.
        """

        return Package.objects.filter(gittree__subdomain=subdomain)

    subdomain.get_packages = _get_packages

    return inject_base_getters(subdomain, _get_users)

def inject_gittree(gittree):
    """
    An injector for setting GitTree object's user getter methods for templates.

    For additional documentation see inject_domain from same module.

    :param  gittree:    GitTree to inject the getter methods into
    :type   gittree:    GitTree model object
    """

    def _get_users(role):
        """
        Returns a list of users with given role for the GitTree object.
        """

        roles = GitTreeRole.objects.filter(role=role, gittree=gittree)
        return [user for group in roles for user in group.user_set.all()]

    return inject_base_getters(gittree, _get_users)

def inject_product(product):
    """
    An injector for setting Product object's user getter methods for templates.

    For additional documentation see inject_domain from same module.

    :param  product:    Product to inject the getter methods into
    :type   product:    Product model object
    """

    def _get_users(role):
        """
        Returns a list of users with given role for the Product object.
        """

        roles = ProductRole.objects.filter(role=role, product=product)
        return [user for group in roles for user in group.user_set.all()]

    return inject_base_getters(product, _get_users)
