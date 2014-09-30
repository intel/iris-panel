# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the read view file for the iris-submissions application.

Views for listing single and multiple item info is contained here.
"""
# pylint: disable=E1101,C0111,W0622,C0301

from collections import defaultdict

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404

from iris.core.models import Submission, BuildGroup


class SubmissionGroup(object):
    """
    Submissions with the same tag name are called SubmissionGroup.
    Submissions in the same group could be submitted by different author in different git tree.
    """
    def __init__(self, submissions):
        assert submissions
        self.subs = submissions
        self.name = self.subs[0].name

    @property
    def products(self):
        return {sbuild.product
                for submission in self.subs
                for sbuild in submission.submissionbuild_set.all()}

    @property
    def display_status(self):
        st0 = [sub.status for sub in self.subs if sub.status not in Submission.STATUS]
        st1 = [sub.status for sub in self.subs if sub.status in Submission.STATUS]
        if not st0:
            if 'DONE' in st1:
                return 'DONE'
            return 'SUMITTED'
        return BuildGroup.STATUS[max(st0)]

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


def group(submissions):
    """
    Returns list of submission groups
    """
    groups = defaultdict(list)
    for sub in submissions:
        groups[sub.name].append(sub)
    groups = [SubmissionGroup(i) for i in groups.values()]
    #FIXME: reverse
    return sorted(groups, key=lambda g: g.updated, reverse=True)


def opened(request):
    """
    All opened submissions
    """
    return render(request, 'submissions/summary.html', {
            'title': 'All submissions',
            'results': group(Submission.objects.all()),
            })


@login_required
def mine(request):
    """
    All my (the logged-in user) opened submissions
    """
    res = Submission.objects.filter(owner=request.user)
    return render(request, 'submissions/summary.html', {
            'title': 'My submissions',
            'results': group(Submission.objects.filter(owner=request.user)),
            })


def search(request):
    """
    Search submissions by keyword
    """
    kw = request.GET.get('kw')
    subs = Submission.objects.filter(
        Q(name__contains=kw) |
        Q(commit__startswith=kw) |
        Q(owner__email__startswith=kw) |
        Q(gittree__gitpath__contains=kw)
        )
    return render(request, 'submissions/summary.html', {
            'title': 'Search result for "%s"' % kw,
            'results': group(subs),
            })


def detail(request, tag):
    """
    Detail info about a submission group identified by certain tag
    """
    groups = group(Submission.objects.filter(name=tag.rstrip('/')))
    if not groups:
        raise Http404

    assert len(groups) == 1  # because it's group by tag
    sgroup = groups[0]
    bgroups = submission_group_to_build_groups(sgroup)

    return render(request, 'submissions/detail.html', {
            'sgroup': sgroup,
            'bgroups': bgroups,
            })


def submission_group_to_build_groups(sgroup):
    """
    Find build groups by submission group (tag)
    """
    return {sbuild.group
            for submission in sgroup.subs
            for sbuild in submission.submissionbuild_set.all()}
