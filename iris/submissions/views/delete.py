# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the deletion view file for the iris-packagedb application.

Views for deleting items are contained here.
"""

# pylint: disable=C0111,W0622

from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required, permission_required

from iris.core.views.common import delete
from iris.core.models import Submission, SubmissionGroup


@login_required()
@permission_required('core.delete_submission', raise_exception=True)
def submissions(request, pkid):
    return delete(request, pkid, Submission, reverse('read_submissions'))

@login_required()
@permission_required('core.delete_submissiongroup', raise_exception=True)
def submissiongroups(request, pkid):
    return delete(request, pkid, SubmissionGroup, reverse('read_submissiongroups'))
