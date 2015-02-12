# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the API view file for the iris-packagedb application.

Views shown by REST Framework under API URLs are defined here.
"""

# pylint: disable=E1101,W0232,C0111,R0901,R0904,W0613
#W0613: Unused argument %r(here it is request)
import json

from rest_framework.decorators import api_view
from django.db.models import Q
from django.http import HttpResponse, HttpResponseNotFound

from iris.core.models import (BuildGroup, SubmissionGroup, Submission)


def get_query(product_name=None, status=None):
    def get_key(value):
        # case insensitive for status
        reverse_dict = dict(
            (v.lower(), k) for k, v in BuildGroup.STATUS.iteritems())
        return reverse_dict.get(value, 'un_exist')
    query_list = []
    if product_name is not None:
        query_list.append(Q(submissionbuild__product__name=product_name))
    if status:
        status_list = [Q(status=get_key(item.lower())) for item in status.split(',')]
        query_list.append(reduce(lambda a, b: a | b, status_list))
    else:
        query_list.extend([~Q(status='33_ACCEPTED'), ~Q(status='36_REJECTED')])

    return reduce(lambda a, b: a&b, query_list)


def get_active_submissions(request, product_name=None):
    '''
    return active Submission list

    active means: submission related with pre-release project, and also
    the project has not been accepted or rejected.

    '''
    if 'status' in request.GET:
        status = request.GET['status']
    else:
        status = None
    bgs = BuildGroup.objects.filter(
        get_query(product_name, status)
        ).prefetch_related(
            'submissionbuild_set__submission__gittree',
            'submissionbuild_set__product',
            'packagebuild_set__package')

    sub_list = []
    for bdg in set(bgs):
        sub_dict = dict()
        if bdg.submissions:
            # becuase submissions are deleted by merging user, then now some
            # buildgroup don't related with submissions
            sub_dict['submission'] = bdg.submissions.pop().name
            sub_dict['status'] = bdg.STATUS[bdg.status]
            sub_dict['packages'] = sorted(list(set(
                            [pb.package.name for pb in bdg.pac_builds])))
            sub_dict['gittrees'] = sorted(bdg.gittrees)
            if product_name is None:
                sub_dict['product'] = bdg.product.name
            sub_list.append(sub_dict)
    sub_list = sorted(sub_list, key=lambda dict: dict['submission'])
    return sub_list


@api_view(['GET'])
def list_submissions(request):
    return HttpResponse(json.dumps(get_active_submissions(request)),
                        content_type="application/json")


@api_view(['GET'])
def list_submissions_by_product(request, project):
    return HttpResponse(
        json.dumps(get_active_submissions(request, project)),
        content_type="application/json")


@api_view(['GET'])
def get_submission(request, project, submission):
    submissions = Submission.objects.filter(
        name=submission,
        submissionbuild__product__name=project
        ).prefetch_related(
            'submissionbuild_set__group__packagebuild_set__package',
            'submissionbuild_set__group__imagebuild_set',
            'owner',
            'gittree',
            )
    if submissions:
        sng = SubmissionGroup(submissions)
        bdg = sng.buildgroup(project)
        packages = [
            ('%s/%s' %(pb.repo, pb.arch), pb.package.name, pb.STATUS[pb.status])
            for pb in bdg.pac_builds if pb.status == 'FAILURE'
            ] if bdg else []
        detail = {
            'submission': submission,
            'target_project': project,
            'commit': sorted(list(sng.commit)),
            'submitter': sorted([u.email for u in sng.owner]),
            'download_url': bdg.download_url if bdg else '',
            'git_trees': sorted([g.gitpath for g in sng.gittree]),
            'images': sorted([
                (i.name, i.STATUS[i.status])
                for i in bdg.imagebuild_set.all()]) if bdg else [],
            'package_build_failures': sorted(packages),
        }
        return HttpResponse(
            json.dumps(detail),
            content_type="application/json")
    else:
        return HttpResponseNotFound(
            json.dumps({'reason': 'submission can not be found'}),
            content_type="application/json")
