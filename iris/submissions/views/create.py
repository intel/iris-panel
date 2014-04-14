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

from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required

from iris.submissions.forms import SubmissionGroupForm


@login_required()
@permission_required('core.add_submissiongroup', raise_exception=True)
def submissiongroups(request):
    if request.method == 'POST':
        request.POST['author'] = request.user
        form = SubmissionGroupForm(request.POST)

        if form.is_valid():
            obj = form.save()
            messages.success(request, 'Creation successful!')
            return redirect(obj)

    form = SubmissionGroupForm()
    form.set_author(request)
    form.set_name()

    return render(request, 'core/create.html', {'form': form})
