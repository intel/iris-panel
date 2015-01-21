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
# pylint: disable=W0232, C0111, R0903, E0213, E1101, C1001
# C1001: Old-style class defined(here it is "Class Meta")
# E1101: %s %r has no %r member (here it is x_set)
# E0213: 29,4:RolesMixin.get_users: Method should have "self" as first argument

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models


def role_users(roles_set, *args):
    '''
        return all users of roles in queryset: role_set
        don't use values() here, because values() doesn't use cache
    '''
    result = {}
    for role in roles_set:
        users = [{arg: getattr(user, arg) for arg in args}
                for user in role.user_set.all()]
        result[role.get_role_display()] = users
    return result


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


class DomainManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Domain(models.Model, RolesMixin):
    """
    Class defining domains, e.g. 'multimedia'.
    """
    objects = DomainManager()

    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    def roles(self, *args):
        return role_users(self.role_set.all(), *args)

    class Meta:
        app_label = APP_LABEL


class SubDomainManager(models.Manager):
    def get_by_natural_key(self, dname, sname):
        return self.get(name=sname, domain__name=dname)


class SubDomain(models.Model):
    """
    Class defining subdomains.
    """
    objects = SubDomainManager()

    name = models.CharField(max_length=255, db_index=True)
    domain = models.ForeignKey(Domain)

    def __unicode__(self):
        return self.name

    def roles(self, *args):
        return role_users(self.subdomainrole_set.all(), *args)

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'domain')

    @property
    def fullname(self):
        return ' / '.join((self.domain.name, self.name))

    def get_packages(self):
        return {package
        for gittree in self.gittree_set.all()
        for package in gittree.packages.all()}


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


class GitTreeManager(models.Manager):
    def get_by_natural_key(self, gitpath):
        return self.get(gitpath=gitpath)


class GitTree(models.Model, RolesMixin):
    """
    Class defining a single git tree information.
    """
    objects = GitTreeManager()

    gitpath = models.CharField(max_length=255, unique=True)
    subdomain = models.ForeignKey(SubDomain)
    licenses = models.ManyToManyField(License)
    packages = models.ManyToManyField('Package')

    def __unicode__(self):
        return self.gitpath

    def roles(self, *args):
        return role_users(self.role_set.all(), *args)

    class Meta:
        app_label = APP_LABEL


class PackageManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Package(models.Model):
    """
    Class defining a package.

    Packages are built from git trees, e.g. git tree 'project' could
    produce packages 'project-base' and 'project-ui'.
    """
    objects = PackageManager()

    name = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return self.name

    def natural_key(self):
        return (self.name,)

    class Meta:
        app_label = APP_LABEL


class ProductManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Product(models.Model):
    """
    A class defining a single product, e.g. Tizen IVI.
    """
    objects = ProductManager()

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    gittrees = models.ManyToManyField(GitTree)

    def __unicode__(self):
        return self.name

    @property
    def latest_snapshot(self):
        snapshots = self.snapshot_set.order_by('-buildid')
        if snapshots:
            return snapshots[0]

    @property
    def latest_daily(self):
        snapshots = self.snapshot_set.exclude(
                        daily_url=None
                        ).order_by(
                        '-daily_url'
                        )
        if snapshots:
            return snapshots[0]

    @property
    def latest_weekly(self):
        snapshots = self.snapshot_set.exclude(
                        weekly_url=None
                        ).order_by(
                        '-weekly_url'
                        )
        if snapshots:
            return snapshots[0]

    class Meta:
        app_label = APP_LABEL


class Image(models.Model):
    """
    Class representing a single image, built for a specific
    architecture relating to a product.
    """

    name = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    arch = models.CharField(max_length=255)
    product = models.ForeignKey(Product)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'target', 'product')
