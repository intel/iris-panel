# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the base view file for the iris-submissions application.

Commonplace views such as index page is contained here.
"""

# pylint: disable=E1101,W0621

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from iris.core.models import Submission, SubmissionGroup


@login_required()
def index(request):
    """
    This view returns the index page for the submissions application.
    """

    return render(request, 'submissions/index.html')

@login_required()
def summary(request):
    """
    Submissions summary page view.

    Requesting the page with ?filter=submissions or ?filter=submissiongroups
    restricts the results accordingly to either Submissions or Groups.
    """

    summary = list()

    if request.GET.get('filter', '') == 'submissions':
        summary.extend(Submission.objects.all())
    elif request.GET.get('filter', '') == 'submissiongroups':
        summary.extend(SubmissionGroup.objects.all())
    else:
        summary.extend(Submission.objects.all())
        summary.extend(SubmissionGroup.objects.all())

    summary = sorted(summary, key=lambda s: s.datetime)

    return render(request, 'submissions/summary.html', {'summary': summary})
