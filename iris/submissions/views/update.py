# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the creation view file for the iris-packagedb application.

Views for adding items are contained here.
"""

# pylint: disable=C0111,W0622

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from iris.core.views.common import update
from iris.core.models import Submission, SubmissionGroup
from iris.submissions.forms import SubmissionForm, SubmissionGroupForm

@login_required()
@permission_required('core.change_submission', raise_exception=True)
def submissions(request, pkid):
    return update(request, pkid, Submission, SubmissionForm)

@login_required()
@permission_required('core.change_submission', raise_exception=True)
def accept_submissions(request, pkid):
    obj = get_object_or_404(Submission, id=pkid)
    obj.status = 'ACCEPTED'
    obj.save()

    return redirect(obj)

@login_required()
@permission_required('core.change_submission', raise_exception=True)
def reject_submissions(request, pkid):
    obj = get_object_or_404(Submission, id=pkid)
    obj.status = 'REJECTED'
    obj.save()

    return redirect(obj)

@login_required()
@permission_required('core.change_submissiongroup', raise_exception=True)
def submissiongroups(request, pkid):
    return update(request, pkid, SubmissionGroup, SubmissionGroupForm)

@login_required()
@permission_required('core.change_submission', raise_exception=True)
def accept_submissiongroups(request, pkid):
    obj = get_object_or_404(SubmissionGroup, id=pkid)
    obj.status = 'ACCEPTED'
    obj.save()

    return redirect(obj)

@login_required()
@permission_required('core.change_submission', raise_exception=True)
def reject_submissiongroups(request, pkid):
    obj = get_object_or_404(SubmissionGroup, id=pkid)
    obj.status = 'REJECTED'
    obj.save()

    return redirect(obj)
