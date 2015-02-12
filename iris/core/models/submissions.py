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
# pylint: disable=W0232, C0111, R0903, no-member, old-style-class
# pylint: disable=no-value-for-parameter, undefined-loop-variable

# This signifies that these models belong to core application.
# Required for splitting up the applications to multiple files.
APP_LABEL = 'core'

from django.db import models
from django.contrib.auth.models import User


DISPLAY_STATUS = {
    'OPENED': 'opened',
    'REJECTED': 'rejected',
    'ACCEPTED': 'accepted',
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

    url = models.URLField(max_length=512)
    log = models.URLField(max_length=512)

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
               for pbuild in self.packagebuild_set.select_related('package').all()}
        sts[packagebuild.natural_key()] = packagebuild.status

        if any([i == 'FAILURE' for i in sts.values()]):
            final = '15_PKGFAILED'
        else:
            final = '10_PKGBUILDING'

        if self.status != final:
            self.status = final
            self.save()

    @property
    def opened(self):
        return self.status not in ['33_ACCEPTED', '36_REJECTED']

    @property
    def accepted(self):
        return self.status == '33_ACCEPTED'

    @property
    def rejected(self):
        return self.status == '36_REJECTED'

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
        # don't use [:1].get() because Slicing a QuerySet that has been
        # evaluated returns a list
        return self.submissionbuild_set.all()[0].product

    @property
    def submissions(self):
        return {sb.submission for sb in self.submissionbuild_set.all()}

    @property
    def gittrees(self):
        return list({
            sb.submission.gittree.gitpath
            for sb in self.submissionbuild_set.all()
        })

    @property
    def download_url(self):
        try:
            return self.imagebuild_set.all()[0].url.split('images')[0]
        except IndexError:
            return ''

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
        'ERROR': 'error',
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
    reason = models.TextField()
    # TODO: update "updated" field when package created and image created

    def __unicode__(self):
        return self.name

    @property
    def display_status(self):
        return dict(self.STATUS, **BuildGroup.STATUS)[self.status]

    @property
    def opened(self):
        groups = {sbuild.group
                    for sbuild in self.submissionbuild_set.select_related(
                        'group', 'submission').all() if sbuild.group
                  }
        if groups:
            not_opened_count = 0
            for group in groups:
                if (group.status == '33_ACCEPTED' or
                    group.status == '36_REJECTED'):
                    not_opened_count += 1
            if not_opened_count == len(groups):
                # all accepted or rejected
                return False
            return True
        else:
            return self.status == 'SUBMITTED'

    @property
    def accepted(self):
        groups = {sbuild.group
                   for sbuild in self.submissionbuild_set.all() if sbuild.group
                  }
        if groups:
            for group in groups:
                if group.status == '33_ACCEPTED':
                    return True
        return False

    @property
    def rejected(self):
        groups = {sbuild.group
                 for sbuild in self.submissionbuild_set.all() if sbuild.group
                 }
        if groups:
            for group in groups:
                if group.status == '36_REJECTED':
                    return True
        return False

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
    def __init__(self, submissions, filter_status=''):
        assert submissions
        self.subs = submissions
        self.name = self.subs[0].name
        self.filter_status = filter_status
        # the init status is submission status when no buildgroup related
        self.status = self.subs[0].display_status

    @classmethod
    def group(cls, submissions, filter_status=''):
        """
        Returns list of submission groups
        """
        groups = defaultdict(list)
        for sub in submissions:
            groups[sub.name].append(sub)
        groups = [cls(i, filter_status) for i in groups.values()]
        groups.sort(key=lambda g: g.updated, reverse=True)
        return groups

    def __unicode__(self):
        return self.name

    @property
    def snapshots(self):
        snapshots = {sbuild.group.snapshot
                     for submission in self.subs
                     for sbuild in submission.submissionbuild_set.all()
                     if sbuild.group.snapshot}
        return sorted(snapshots,
                      key=lambda snapshot: snapshot.product.name)

    @property
    def product_status(self):
        product_groups = {}
        def set_values():
            if sbuild.product in product_groups:
                # make sure one product only related with
                # one pre-relsese project
                assert product_groups[sbuild.product] == sbuild.group
            else:
                product_groups[sbuild.product] = sbuild.group

        for sub in self.subs:
            for sbuild in sub.submissionbuild_set.all():
                if (self.filter_status == DISPLAY_STATUS['OPENED'] and
                        sbuild.group.opened):
                    set_values()

                if (self.filter_status == DISPLAY_STATUS['ACCEPTED'] and
                        sbuild.group.accepted):
                    set_values()

                if (self.filter_status == DISPLAY_STATUS['REJECTED'] and
                       sbuild.group.rejected):
                    set_values()
                if not self.filter_status:
                    # no status ,get all
                    set_values()

        return product_groups

    @property
    def owner(self):
        return {s.owner for s in self.subs}

    @property
    def gittree(self):
        return {s.gittree for s in self.subs}

    def buildgroup(self, product_name):
        bgs = BuildGroup.objects.filter(
            submissionbuild__submission__name=self.name,
            submissionbuild__product__name=product_name
        )
        assert len(set(bgs)) in [0, 1]
        if bgs:
            return bgs[0]
        else:
            return None

    @property
    def commit(self):
        return {s.commit for s in self.subs}

    @property
    def gittree_commit(self):
        return {(s.gittree, s.commit) for s in self.subs}

    @property
    def updated(self):
        return max([s.updated for s in self.subs])

    @property
    def created(self):
        return min([s.created for s in self.subs])


class Snapshot(models.Model):

    product = models.ForeignKey('Product')
    buildid = models.CharField(max_length=128)
    started_time = models.DateTimeField()
    finished_time = models.DateTimeField(blank=True, null=True)
    url = models.URLField(max_length=512, blank=True, null=True)
    daily_url = models.URLField(max_length=512, blank=True, null=True)
    weekly_url = models.URLField(max_length=512, blank=True, null=True)

    @property
    def submissions(self):
        return {sb.submission
                for buildgroup in self.buildgroup_set.all()
                for sb in buildgroup.submissionbuild_set.all()
               }

    @classmethod
    def snapshots_with_same_product(cls, pro_obj):
        return Snapshot.objects.filter(
            product=pro_obj
            ).exclude(
                finished_time=None
                ).order_by(
                    '-finished_time'
                    )

    class Meta:
        app_label = APP_LABEL
        unique_together = ('product', 'buildid')
