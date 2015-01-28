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
from collections import OrderedDict

from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.http import HttpResponse

from iris.core.models import (BuildGroup, GitTree, Package, Product)


def get_submission_name(buildgroup):
    submissions = {sbuild.submission.name
                    for sbuild in buildgroup.submissionbuild_set.all()}

    assert len(submissions) == 1
    return submissions.pop()


def get_packages(buildgroup):
    packages = {pb.package.name
                for pb in buildgroup.packagebuild_set.all()}
    return list(packages)


def get_query(request, project):
    def get_key(value):
        # case insensitive for status
        reverse_dict = dict((v.lower(), k)
                        for k, v in BuildGroup.STATUS.iteritems())
        return reverse_dict.get(value, 'un_exist')

    query = Q(submissionbuild__product__name=project)
    query &= ~Q(status='33_ACCEPTED')
    query &= ~Q(status='36_REJECTED')
    if 'status' in request.GET:
        query &= Q(status=get_key(request.GET['status'].lower()))
    return query


@api_view(['GET'])
def list_submissions_by_product(request, project):

    bgs = BuildGroup.objects.filter(
        get_query(request, project)
        ).prefetch_related(
        'submissionbuild_set__submission',
        'packagebuild_set__package')

    sub_list = []
    for bg in bgs:
        sub_dict = dict()
        sub_dict['submission'] = get_submission_name(bg)
        sub_dict['status'] = bg.STATUS[bg.status]
        sub_dict['packages'] = get_packages(bg)
        sub_list.append(sub_dict)
    sub_list = sorted(sub_list, key=lambda dict: dict['submission'])
    return HttpResponse(json.dumps(sub_list), content_type="application/json")
