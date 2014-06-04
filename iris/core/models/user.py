# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the group related Django database model module for the iris-core.

Models related to user groups go here.
"""

# Disabling class checks for the sake of Django specific Meta classes.
# pylint: disable=W0232, C0111, R0903, W0612, W0613, E1101

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from iris.core.models import Domain, SubDomain, GitTree, Product


class UserProfile(models.Model):
    """
    User information that is application specific and outside User model.
    """

    User._meta.get_field("username").max_length = 225
    user = models.OneToOneField(User)

    def __unicode__(self):
        return self.user

    class Meta:
        app_label = APP_LABEL


def create_user_profile(sender, instance, created, **kwargs):
    """
    Post save signal handler for automatically creating an user profile
    upon each user creation, if one does not exist at the time.
    """

    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)


def parties():
    """
    Returns possible parties a user can belong to.
    """

    _parties = (
        ('INTEL', 'Intel'),
        ('SAMSUNG', 'Samsung'),
        ('TIZEN', 'Tizen.org (OSS community)'),
    )

    return _parties


class UserParty(Group):
    """
    Group role model describing which parties an user belongs to.

    User could be e.g. part of both Intel and Tizen OS initiative.
    """

    party = models.CharField(max_length=15, choices=parties())

    def __unicode__(self):
        return self.party

    class Meta:
        app_label = APP_LABEL


def roles():
    """
    Returns possible roles a user can have regarding items below.
    """

    _roles = (
        ('ARCHITECT', 'Architect'),
        ('MAINTAINER', 'Maintainer'),
        ('DEVELOPER', 'Developer'),
        ('REVIEWER', 'Reviewer'),
        ('INTEGRATOR', 'Integrator'),
    )

    return _roles


class ProductRole(Group):
    """
    Group role model concerning a product such as Tizen IVI etc.
    """

    role = models.CharField(max_length=15, choices=roles(), db_index=True)
    product = models.ForeignKey(Product)

    def __unicode__(self):
        return '%s: %s' % (self.role, self.product.name)

    class Meta:
        app_label = APP_LABEL


class DomainRole(Group):
    """
    Group role model concerning a domain such as Security etc.
    """

    role = models.CharField(max_length=15, choices=roles(), db_index=True)
    domain = models.ForeignKey(Domain)

    def __unicode__(self):
        return '%s: %s' % (self.role, self.domain.name)

    class Meta:
        app_label = APP_LABEL


class SubDomainRole(Group):
    """
    Group role model concerning subdomains.
    """

    role = models.CharField(max_length=15, choices=roles(), db_index=True)
    subdomain = models.ForeignKey(SubDomain)

    def __unicode__(self):
        return '%s: %s' % (self.role, self.subdomain.name)

    class Meta:
        app_label = APP_LABEL


class GitTreeRole(Group):
    """
    Group role model concerning git trees.
    """

    role = models.CharField(max_length=15, choices=roles(), db_index=True)
    gittree = models.ForeignKey(GitTree, related_name='role_set')

    def __unicode__(self):
        return '%s: %s' % (self.role, self.gittree.gitpath)

    class Meta:
        app_label = APP_LABEL
