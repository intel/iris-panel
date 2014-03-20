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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required()
def index(request):
    """
    This view returns the index page for the submissions application.
    """

    return render(request, 'submissions/index.html')
