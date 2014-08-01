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

    STATUS = {
        'SUCCESS': 'Succeeded',
        'FAILURE': 'Failed',
        }

    package = models.ForeignKey('Package')

    target = models.TextField()
    arch = models.TextField()
    status = models.CharField(max_length=64, choices=STATUS.items())

    log = models.URLField()

    @property
    def display_status(self):
        return self.STATUS[self.status]

    def __unicode__(self):
        return self.status

    class Meta:
        app_label = APP_LABEL


class ImageBuild(models.Model):
    """
    Class representing the image building step of the build process.
    """

    STATUS = {
        'SUCCESS': 'Succeeded',
        'FAILURE': 'Failed',
        }

    name = models.TextField()
    repo = models.CharField(max_length=255)
    status = models.CharField(max_length=64, choices=STATUS.items())

    group = models.ForeignKey('BuildGroup')

    url = models.URLField()
    log = models.URLField()

    @property
    def display_status(self):
        return self.STATUS[self.status]

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
    status = models.CharField(max_length=64, choices=TESTSTATUS)

    def __unicode__(self):
        return self.status

    class Meta:
        app_label = APP_LABEL


class Submission(models.Model):
    """
    Class representing a single submission for review.

    A single submission is a tag pushed for e.g. review or release.
    """

    STATUS = {
        'SUBMITTED': 'Submitted',
        'PROCESSING': 'Processing',
        'DONE': 'Done',
        }
    # when all build groups related to this submission are in final states
    # this submission can be set to DONE state

    # tag name, submissions with the same name is a submission group
    name = models.CharField(max_length=255, db_index=True)

    status = models.CharField(max_length=64, db_index=True,
                              choices=STATUS.items())

    owner = models.ForeignKey(User)
    gittree = models.ForeignKey('GitTree')
    commit = models.CharField(max_length=255, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @property
    def display_status(self):
        return self.STATUS[self.status]

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'gittree')


class SubmissionBuild(models.Model):
    """
    Class representing a build of a submission against certain product.
    """

    submission = models.ForeignKey('Submission')
    product = models.ForeignKey('Product')

    group = models.ForeignKey('BuildGroup')
    pbuilds = models.ManyToManyField('PackageBuild')

    class Meta:
        app_label = APP_LABEL
        unique_together = ('submission', 'product')


class BuildGroup(models.Model):
    """
    Class representing a group of builds which could be accepted
    together by a release engineer.
    """

    STATUS = {
        '10_PKGBUILDING': 'Package building',
        '15_PKGFAILED': 'Package building failed',

        '20_IMGBUILDING': 'Image building',
        '25_IMGFAILED': 'Image build failed',

        '30_READY': 'Ready for acceptance',
        '33_ACCEPTED': 'Accepted',
        '36_REJECTED': 'Rejected',
        }
    # Final states are: ACCEPTED, REJECTED

    # pre-release project name
    name = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=64, db_index=True, choices=STATUS.items())

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # repa operator: accepted/rejected by
    operator = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL)
    operated_on = models.DateTimeField(blank=True, null=True)
    operate_reason = models.TextField()

    snapshot = models.URLField()

    def __unicode__(self):
        return self.name

    @property
    def display_status(self):
        return self.STATUS[self.status]

    class Meta:
        app_label = APP_LABEL


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
    product = models.ForeignKey('Product', blank=True, null=True,
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
