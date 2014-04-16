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
from iris.core.models import Submission, SubmissionGroup


@login_required()
def submissions(request, pkid=None):
    if pkid:
        return render(request, 'submissions/read/single/submission.html',
                {'submission': get_object_or_404(Submission, id=pkid)})
    else:
        return render(request, 'submissions/read/multiple/submissions.html',
                {'submissions': Submission.objects.all()})

@login_required()
def submissiongroups(request, pkid=None):
    if pkid:
        return render(request, 'submissions/read/single/submissiongroup.html',
                {'submissiongroup': get_object_or_404(SubmissionGroup, id=pkid)})
    else:
        return render(request, 'submissions/read/multiple/submissiongroups.html',
                {'submissiongroups': SubmissionGroup.objects.all()})
