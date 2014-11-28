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
from collections import defaultdict

# Disabling class checks for the sake of Django specific Meta classes.
# pylint: disable=W0232, C0111, R0903

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models
from django.contrib.auth.models import User

FINAL_STATUS = {
    '15_PKGFAILED': 'failed',
    '25_IMGFAILED': 'failed',
    '36_REJECTED': 'failed',

    '33_ACCEPTED': 'success',

    '10_PKGBUILDING': 'building',
    '20_IMGBUILDING': 'building',
    'SUBMITTED': 'building',
    }

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
    status = models.CharField(max_length=64, choices=STATUS.items())
    repo = models.CharField(max_length=255, db_index=True)
    arch = models.CharField(max_length=255, db_index=True)

    group = models.ForeignKey('BuildGroup')

    url = models.URLField(max_length=512)
    log = models.URLField(max_length=512)

    @property
    def display_status(self):
        return self.STATUS[self.status]

    def __unicode__(self):
        return u'%s: %s' % (unicode(self.package), self.status)

    def natural_key(self):
        return self.package.natural_key() + (
            self.repo,
            self.arch,
            ) + self.group.natural_key()

    class Meta:
        app_label = APP_LABEL
        unique_together = ('package', 'repo', 'arch', 'group')


class ImageBuild(models.Model):
    """
    Class representing the image building step of the build process.
    """

    STATUS = {
        'BUILDING': 'Building',
        'SUCCESS': 'Succeeded',
        'FAILURE': 'Failed',
        }

    name = models.CharField(max_length=255, db_index=True)
    repo = models.CharField(max_length=255)
    status = models.CharField(max_length=64, choices=STATUS.items())

    group = models.ForeignKey('BuildGroup')

    url = models.URLField()
    log = models.URLField()

    @property
    def display_status(self):
        return self.STATUS[self.status]

    def __unicode__(self):
        return u'%s: %s' % (self.name, self.status)

    def natural_key(self):
        return (self.name,) + self.group.natural_key()

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'group')


class BuildGroupManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class BuildGroup(models.Model):
    """
    Class representing a group of builds which could be accepted
    together by a release engineer.
    """
    objects = BuildGroupManager()

    STATUS = {
        '10_PKGBUILDING': 'Package building',
        '15_PKGFAILED': 'Package building failed',

        '20_IMGBUILDING': 'Image building',
        '25_IMGFAILED': 'Image build failed',

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
    operator = models.CharField(
        max_length=255, db_index=True, blank=True, null=True)
    operated_on = models.DateTimeField(blank=True, null=True)
    operate_reason = models.TextField()
    snapshot = models.ForeignKey('Snapshot', blank=True, null=True)

    # TODO: obs pre-release project url
    # url = models.URLField()

    def __unicode__(self):
        return self.name

    @property
    def display_status(self):
        return self.STATUS[self.status]

    def check_packages_status(self, packagebuild):
        """
        Check all packages building status
        Argument `packagebuild` is the newest comming package build
        """
        sts = {pbuild.natural_key(): pbuild.status
               for pbuild in self.packagebuild_set.all()}
        sts[packagebuild.natural_key()] = packagebuild.status

        if any([i == 'FAILURE' for i in sts.values()]):
            final = '15_PKGFAILED'
        else:
            final = '10_PKGBUILDING'

        if self.status != final:
            self.status = final
            self.save()

    def check_images_status(self, imagebuild):
        """
        Check all images building status
        Argument `status` is the newest comming image status
        """
        sts = {ibuild.natural_key(): ibuild.status
               for ibuild in self.imagebuild_set.all()}
        sts[imagebuild.natural_key()] = imagebuild.status

        if any([i == 'FAILURE' for i in sts.values()]):
            final = '25_IMGFAILED'
        else:
            final = '20_IMGBUILDING'

        if self.status != final:
            self.status = final
            self.save()

    def populate_status(self):
        """
        Populate this BuildGroup's status to related Submissions
        """
        for sbuild in self.submissionbuild_set.all().order_by('id'):
            if sbuild.submission.status != self.status:
                sbuild.submission.status = self.status
                sbuild.submission.save()

    @property
    def product(self):
        """
        All product attrs of submissionbuild_set must be equal,
        othewise they can be put into a build group to build.
        """
        return self.submissionbuild_set.all()[:1].get().product

    def natural_key(self):
        return (self.name,)

    class Meta:
        app_label = APP_LABEL


class SubmissionManager(models.Manager):
    def get_by_natural_key(self, tag, gitpath):
        return self.get(name=tag, gittree__gitpath=gitpath)


class Submission(models.Model):
    """
    Class representing a single submission for review.

    A single submission is a tag pushed for e.g. review or release.
    """
    objects = SubmissionManager()

    STATUS = {
        'SUBMITTED': 'Submitted',
        }
    # when all build groups related to this submission are in final states
    # this submission can be set to DONE state

    # tag name, submissions with the same name is a submission group
    name = models.CharField(max_length=255, db_index=True)

    status = models.CharField(
        max_length=64, db_index=True,
        choices=STATUS.items()+BuildGroup.STATUS.items())

    owner = models.ForeignKey(User)
    gittree = models.ForeignKey('GitTree')
    commit = models.CharField(max_length=255, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # TODO: update "updated" field when package created and image created

    def __unicode__(self):
        return self.name

    @property
    def display_status(self):
        return dict(self.STATUS, **BuildGroup.STATUS)[self.status]

    class Meta:
        app_label = APP_LABEL
        unique_together = ('name', 'gittree')
        permissions = (('publish_events', 'Can publish events'),)


class SubmissionBuild(models.Model):
    """
    Class representing a build of a submission against certain product.
    """

    submission = models.ForeignKey('Submission')
    product = models.ForeignKey('Product')

    group = models.ForeignKey('BuildGroup')

    class Meta:
        app_label = APP_LABEL
        unique_together = ('submission', 'product')


class SubmissionGroup(object):
    """
    Submissions with the same tag name are called SubmissionGroup.

    Submissions in the same group could be submitted by different
    author in different git tree.

    SubmissionGroup is just a business model without separated
    database table with it. It's a group view of Submission
    model.
    """
    def __init__(self, submissions):
        assert submissions
        self.subs = submissions
        self.name = self.subs[0].name

    @classmethod
    def group(cls, submissions):
        """
        Returns list of submission groups
        """
        groups = defaultdict(list)
        for sub in submissions:
            groups[sub.name].append(sub)
        groups = [cls(i) for i in groups.values()]
        groups.sort(key=lambda g: g.updated, reverse=True)
        return groups

    def __unicode__(self):
        return self.name

    @property
    def products(self):
        return {sbuild.product
                for submission in self.subs
                for sbuild in submission.submissionbuild_set.all()}

    @property
    def _cal_status(self):
        st0 = [sub.status for sub in self.subs
            if sub.status not in Submission.STATUS]
        st1 = [sub.status for sub in self.subs
            if sub.status in Submission.STATUS]
        if st0:
            st = max(st0)
        else:
            st = 'DONE' if 'DONE' in st1 else 'SUBMITTED'
        return st

    @property
    def display_status(self):
        return dict(Submission.STATUS, **BuildGroup.STATUS)[self._cal_status]

    @property
    def display_colors(self):
        return FINAL_STATUS[self._cal_status]

    @property
    def owner(self):
        if self.count > 1:
            return {s.owner for s in self.subs}
        return self.subs[0].owner

    @property
    def gittree(self):
        if self.count > 1:
            return {s.gittree for s in self.subs}
        return self.subs[0].gittree

    @property
    def commit(self):
        if self.count > 1:
            return {s.commit for s in self.subs}
        return self.subs[0].commit

    @property
    def gittree_commit(self):
        if self.count > 1:
            return {(s.gittree, s.commit) for s in self.subs}
        return [(self.subs[0].gittree, self.subs[0].commit)]

    @property
    def updated(self):
        return max([s.updated for s in self.subs])

    @property
    def created(self):
        return min([s.created for s in self.subs])

    @property
    def count(self):
        return len(self.subs)


class Snapshot(models.Model):

    product = models.ForeignKey('Product')
    buildid= models.CharField(max_length=128)
    started_time = models.DateTimeField()
    finished_time = models.DateTimeField(blank=True, null=True)
    url = models.URLField(max_length=512, blank=True, null=True)
    daily_url = models.URLField(max_length=512, blank=True, null=True,
                                db_index=True)
    weekly_url = models.URLField(max_length=512, blank=True, null=True,
                                db_index=True)

    class Meta:
        app_label = APP_LABEL
        unique_together = ('product', 'buildid')
