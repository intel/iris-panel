# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the packaging related Django database model module for the iris-core.

Models related to packaging and version control go here.
"""

# Disabling class checks for the sake of Django specific Meta classes.
# pylint: disable=W0232, C0111, R0903

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models


class RolesMixin(object):

    def get_users(rolestring):
        def getter(self):
            # role_set is defined by "related_name" of corresponding role model
            for role in self.role_set.all():
                if role.role == rolestring:
                    return role.user_set.all()
            return ()
        return getter

    get_architects = get_users('ARCHITECT')
    get_maintainers = get_users('MAINTAINER')
    get_developers = get_users('DEVELOPER')
    get_reviewers = get_users('REVIEWER')
    get_integrators = get_users('INTEGRATOR')


class Domain(models.Model, RolesMixin):
    """
    Class defining domains, e.g. 'multimedia'.
    """

    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL


class SubDomain(models.Model):
    """
    Class defining subdomains.
    """

    name = models.CharField(max_length=255, db_index=True)
    domain = models.ForeignKey(Domain)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'domain')


class License(models.Model):
    """
    Class defining license information.

    Aims to be compatible with Fossology tool models.
    """

    fullname = models.CharField(max_length=255, db_index=True)
    shortname = models.CharField(max_length=255, unique=True)
    text = models.TextField()

    def __unicode__(self):
        return self.fullname if self.fullname else self.shortname

    class Meta:
        app_label = APP_LABEL


class GitTree(models.Model, RolesMixin):
    """
    Class defining a single git tree information.
    """

    gitpath = models.CharField(max_length=255, unique=True)
    subdomain = models.ForeignKey(SubDomain)
    licenses = models.ManyToManyField(License)
    packages = models.ManyToManyField('Package')

    def __unicode__(self):
        return self.gitpath

    class Meta:
        app_label = APP_LABEL


class Package(models.Model):
    """
    Class defining a package.

    Packages are built from git trees, e.g. git tree 'project' could
    produce packages 'project-base' and 'project-ui'.
    """

    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL


class Product(models.Model):
    """
    A class defining a single product, e.g. Tizen IVI.
    """

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    gittrees = models.ManyToManyField(GitTree)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL


class Image(models.Model):
    """
    Class representing a single image, built for a specific
    architecture relating to a product.
    """

    name = models.TextField()
    target = models.TextField()
    arch = models.TextField()
    product = models.ForeignKey(Product)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL
