# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the submission related Django database model module for the iris-core.

Models related to submissions and acceptance go here.
"""

# Disabling class checks for the sake of Django specific Meta classes.
# pylint: disable=W0232, C0111, R0903

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from iris.core.models import GitTree, Package, Product, Image


class Log(models.Model):
    """
    Class representing a single log produced from a
    build of image or package build or test

    Storing log data into the database or providing just
    external URL hasn't been decided yet.
    """

    url = models.URLField()

    def __unicode__(self):
        return self.url

    class Meta:
        app_label = APP_LABEL


class PackageBuild(models.Model):
    """
    Class representing the package building step of the build process.

    A single PackageBuild model represents the build process of manufacturing
    a single package for a relevant architectures, e.g. amd_64 and i386.
    """

    BUILDSTATUS = (
        ('SUCCESS', 'Succeeded'),
        ('FAILURE', 'Failed'),
    )

    package = models.ForeignKey(Package)
    target = models.TextField()
    arch = models.TextField()
    log = models.OneToOneField(Log, blank=True, null=True,
                                on_delete=models.SET_NULL)
    status = models.CharField(max_length=8, choices=BUILDSTATUS)

    def __unicode__(self):
        return self.status

    class Meta:
        app_label = APP_LABEL


class ImageBuild(models.Model):
    """
    Class representing the image building step of the build process.
    """

    BUILDSTATUS = (
        ('SUCCESS', 'Succeeded'),
        ('FAILURE', 'Failed'),
    )

    image = models.ForeignKey(Image)
    name = models.TextField()
    log = models.OneToOneField(Log, blank=True, null=True,
                                on_delete=models.SET_NULL)
    status = models.CharField(max_length=8, choices=BUILDSTATUS)

    def __unicode__(self):
        return self.status

    class Meta:
        app_label = APP_LABEL


class TestResult(models.Model):
    """
    Class representing the testing step of the build process.
    """

    TESTSTATUS = (
        ('SUCCESS', 'Succeeded'),
        ('NOREGRESSIONS', 'No regressions'),
        ('FAILURE', 'Failed'),
    )

    name = models.TextField()
    log = models.OneToOneField(Log, blank=True, null=True,
                                on_delete=models.SET_NULL)
    status = models.CharField(max_length=16, choices=TESTSTATUS)

    def __unicode__(self):
        return self.status

    class Meta:
        app_label = APP_LABEL


class Submission(models.Model):
    """
    Class representing a single submission for review.

    A single submission is a tag pushed for e.g. review or release.
    """

    SUBMISSIONSTATUS = (
        ('SUBMITTED', 'Submitted'),
        ('PKGBUILDING', 'Package building'),
        ('PKGFAILED', 'Package building failed'),
        ('IMGBUILDING', 'Image building'),
        ('IMGFAILED', 'Image build failed'),
        ('TESTING', 'Testing package'),
        ('TESTINGFAILED', 'Testing failed'),
        ('READY', 'Ready for acceptance'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('LOCKED', 'Locked'),
    )

    name = models.CharField(max_length=80, db_index=True)
    commit = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=16, choices=SUBMISSIONSTATUS,
                              db_index=True)
    product = models.ForeignKey(Product, blank=True, null=True,
                                on_delete=models.SET_NULL)
    gittree = models.ManyToManyField(GitTree, blank=True)
    pbuilds = models.ManyToManyField(PackageBuild, blank=True)
    ibuilds = models.ManyToManyField(ImageBuild, blank=True)
    testresults = models.ManyToManyField(TestResult, blank=True)
    submitters = models.ManyToManyField(User)
    comment = models.TextField(blank=True)
    obj_type = 'Submission'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('read_submissions', args=(self.id,))

    class Meta:
        app_label = APP_LABEL

    # workaround to stop pylint complaint
    # class 'Submission' has no 'objects' name
    objects = models.Manager()

class SubmissionGroup(models.Model):
    """
    Class representing a group of submissons made by a release engineer.
    """

    SUBMISSIONGROUPSTATUS = (
        ('NEW', 'New'),
        ('IMGBUILDING', 'Image building'),
        ('IMGFAILED', 'Image build failed'),
        ('TESTING', 'Testing package'),
        ('TESTINGFAILED', 'Testing failed'),
        ('READY', 'Ready for acceptance'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
    )

    name = models.CharField(max_length=80, db_index=True)
    author = models.ForeignKey(User)
    product = models.ForeignKey(Product, blank=True, null=True,
                                on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    submissions = models.ManyToManyField(Submission)
    status = models.CharField(max_length=16, choices=SUBMISSIONGROUPSTATUS)
    obj_type = 'SubmissionGroup'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('read_submissiongroups', args=(self.id,))

    class Meta:
        app_label = APP_LABEL
