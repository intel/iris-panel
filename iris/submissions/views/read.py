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

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import (
    Http404, HttpResponseRedirect, HttpResponseBadRequest, HttpResponse)
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError

from iris.core.models import (
    Submission, BuildGroup, SubmissionGroup, Snapshot, Product, DISPLAY_STATUS)


def index(request):
    """
    Index page of Submissions app.
    If a user logged-in, redirect to "my submissions" page,
    otherwise redirect to "opened submissions" page.
    """
    if request.user.is_authenticated():
        url = reverse('my_submissions')
    else:
        url = reverse('opened_submissions')
    return HttpResponseRedirect(url)


def get_submissions(**query):
    return [sub for sub in Submission.objects.select_related(
        'owner', 'gittree').filter(**query).prefetch_related(
            'submissionbuild_set__product',
            'submissionbuild_set__group',
            'submissionbuild_set__group__snapshot',
            )]


def opened(request):
    """
    All opened submissions
    """
    subs = [sub for sub in get_submissions() if sub.opened]
    return render(request, 'submissions/summary.html', {
        'title': 'All open submissions',
        'results': SubmissionGroup.group(subs, DISPLAY_STATUS['OPENED']),
        'keyword': 'status:%s' % DISPLAY_STATUS['OPENED'],
        })


def accepted(request):
    """
    All accepted submissions
    """
    subs = [sub for sub in get_submissions() if sub.accepted]
    return render(request, 'submissions/summary.html', {
        'title': 'All accepted submissions',
        'results': SubmissionGroup.group(subs, DISPLAY_STATUS['ACCEPTED']),
        'keyword': 'status:%s' % DISPLAY_STATUS['ACCEPTED'],
        'show_snapshot': True,
        })


def rejected(request):
    """
    All rejected submissions
    """
    subs = [sub for sub in get_submissions() if sub.rejected]
    return render(request, 'submissions/summary.html', {
        'title': 'All rejected submissions',
        'results': SubmissionGroup.group(subs, DISPLAY_STATUS['REJECTED']),
        'keyword': 'status:%s' % DISPLAY_STATUS['REJECTED'],
        })


@login_required
def mine(request):
    """
    All my (the logged-in user) opened submissions
    TODO: add menu as all did, show opened, rejected, accepted
    """
    subs = [sub for sub in get_submissions(owner=request.user) if sub.opened]
    return render(request, 'submissions/summary.html', {
        'title': 'My submissions',
        'results': SubmissionGroup.group(subs, DISPLAY_STATUS['OPENED']),
        'keyword': 'status:%s owner:%s' % (DISPLAY_STATUS['OPENED'],
                                           request.user.email)
        })


def parse_query_string(query_string):
    """
    validate keyworkd used for search submission

    support keyword format:
    1. key:value key:value(more key:value separated with space) value
       support keyes: status, name, owner, gittree
    2. key:value key:value(more key:value separated with space)
    3. value
    4. only value means the value can be name, owner, gittree or commit
    5. Only one value with no key is supported
    """
    kw = {}
    for item in query_string.split():
        if ':' not in item:
            if kw.get('query'):
                return
            kw['query'] = item
            continue

        key, val = item.split(':', 1)
        key = key.lower()
        if key not in ('status', 'name', 'owner', 'gittree'):
            return
        if key == 'status' and val not in DISPLAY_STATUS.values():
            return
        kw[key] = val
    return kw


def validate_search(request):
    """ Ajax view for validte keyword before search """
    if request.GET.get('kw') and parse_query_string(request.GET.get('kw')):
        return HttpResponse('ok')
    return HttpResponseBadRequest('error')


def make_query_conditions(kw):
    fields = {
        'name': ['name__contains'],
        'owner': [
            'owner__email__startswith',
            'owner__first_name__contains',
            'owner__last_name__contains',
            ],
        'gittree': ['gittree__gitpath__contains'],
        'query': [
            'name__contains',
            'owner__email__startswith',
            'owner__first_name__contains',
            'owner__last_name__contains',
            'commit__startswith',
            'gittree__gitpath__contains',
            ],
        }

    def _and(*args):
        return reduce(lambda i, j: i & j, *args)

    def _or(*args):
        return reduce(lambda i, j: i | j, *args)

    return _and([
        _or([Q(**{field: val}) for field in fields[key]])
        for key, val in kw.items()])


def search(request):
    """Search submissions by keyword """
    querystring = request.GET.get('kw')
    if not querystring:
        return HttpResponseBadRequest('error')
    kw = parse_query_string(querystring)
    st = kw.pop('status', None) if kw else None
    subs = Submission.objects.select_related('owner', 'gittree', 'product')
    if kw:
        query = make_query_conditions(kw)
        subs = subs.filter(query)
    else:
        subs = subs.all()

    show_snapshot = False
    if st:
        if st == DISPLAY_STATUS['OPENED']:
            subs = {sub for sub in subs if sub.opened}
        if st == DISPLAY_STATUS['REJECTED']:
            subs = {sub for sub in subs if sub.rejected}
        if st == DISPLAY_STATUS['ACCEPTED']:
            subs = {sub for sub in subs if sub.accepted}
            show_snapshot = True

    return render(
        request,
        'submissions/summary.html',
        {'title': 'Search result for "%s"' % querystring,
         'results': SubmissionGroup.group(subs, st),
         'keyword': querystring,
         'show_snapshot': show_snapshot
        })


def detail(request, tag):
    """
    Detail info about a submission group identified by certain tag
    """
    groups = SubmissionGroup.group(
        Submission.objects.filter(name=tag.rstrip('/')))
    if not groups:
        raise Http404

    assert len(groups) == 1  # because it's group by tag
    sgroup = groups[0]
    bgroups = submission_group_to_build_groups(sgroup)

    return render(
        request,
        'submissions/detail.html',
        {'sgroup': sgroup,
         'bgroups': bgroups,
        })


def submission_group_to_build_groups(sgroup):
    """
    Find build groups by submission group (tag)
    """
    return {sbuild.group
            for submission in sgroup.subs
            for sbuild in submission.submissionbuild_set.all()}


def snapshot_by_product(request, product_id, offset=0, limit=10):
    """
        if change limit, please also update the value in template:
        iris/submissions/templates/submissions/read/multiple/snapshots.html
    """

    pro = Product.objects.get(pk=product_id)
    all_snapshots = Snapshot.snapshots_with_same_product(pro)

    offset = int(offset)
    limit = int(limit)
    end = offset + limit
    more_data = True
    if end >= len(all_snapshots):
        more_data = False

    snapshots = all_snapshots[offset:end]
    for snapshot in snapshots:
        groups = SubmissionGroup.group(snapshot.submissions)
        snapshot.groups = sorted(groups,
                                key=lambda group: group.name,
                                reverse=True)

    if request.is_ajax():
        response = render(request, 'submissions/read/multiple/snapshot_submissions.html', {
                'snapshots': snapshots,
                'product': pro,
        })
        response['X-No-More'] = more_data
        return response
    else:
        return render(request, 'submissions/read/multiple/snapshots.html', {
                'snapshots': snapshots,
                'product': pro,
                'more_data': more_data,
            })


def snapshot(request, pkid):
    snapshot = get_object_or_404(Snapshot, id=pkid)
    groups = SubmissionGroup.group(snapshot.submissions)

    # get snapshots with the same product
    snapshots = list(Snapshot.snapshots_with_same_product(snapshot.product))
    st_len = len(snapshots)
    first_item = False
    last_item = False
    pre_st = None
    next_st = None
    current_index = snapshots.index(snapshot)
    if current_index == 0:
        first_item = True
    else:
        pre_st = snapshots[current_index-1]
    if current_index == (st_len -1):
        last_item = True
    else:
        next_st = snapshots[current_index+1]
    return render(request, 'submissions/read/single/snapshot.html', {
            'snapshot': snapshot,
            'groups': groups,
            'pre_st': pre_st,
            'next_st': next_st,
            'first_item': first_item,
            'last_item': last_item,
            })
