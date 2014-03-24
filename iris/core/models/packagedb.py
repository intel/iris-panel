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


class Domain(models.Model):
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

    name = models.TextField()
    domain = models.ForeignKey(Domain)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL


class License(models.Model):
    """
    Class defining license information.

    Aims to be compatible with Fossology tool models.
    """

    fullname = models.TextField()
    shortname = models.TextField()
    url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    text = models.TextField()
    active = models.BooleanField(default=True)
    text_updatable = models.BooleanField(default=False)
    md5 = models.CharField(max_length=32)
    detector_type = models.IntegerField(default=0)

    def __unicode__(self):
        return self.fullname if self.fullname else self.shortname

    class Meta:
        app_label = APP_LABEL


class GitTree(models.Model):
    """
    Class defining a single git tree information.
    """

    gitpath = models.TextField()
    subdomain = models.ForeignKey(SubDomain)
    licenses = models.ManyToManyField(License)

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

    name = models.TextField()
    gittree = models.ForeignKey(GitTree)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = APP_LABEL


class Product(models.Model):
    """
    A class defining a single product, e.g. Tizen IVI.
    """

    name = models.TextField()
    short = models.TextField()
    state = models.TextField()
    targets = models.TextField()
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
