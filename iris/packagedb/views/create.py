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

from iris.core.views.common import create
from django.contrib.auth.decorators import login_required, permission_required
from iris.packagedb.forms import (DomainForm, SubDomainForm, LicenseForm,
        GitTreeForm, PackageForm, ProductForm, ImageForm)


@login_required()
@permission_required('core.add_domain', raise_exception=True)
def domain(request):
    return create(request, DomainForm)

@login_required()
@permission_required('core.add_subdomain', raise_exception=True)
def subdomain(request):
    return create(request, SubDomainForm)

@login_required()
@permission_required('core.add_license', raise_exception=True)
def license(request):
    return create(request, LicenseForm)

@login_required()
@permission_required('core.add_gittree', raise_exception=True)
def gittree(request):
    return create(request, GitTreeForm)

@login_required()
@permission_required('core.add_package', raise_exception=True)
def package(request):
    return create(request, PackageForm)

@login_required()
@permission_required('core.add_product', raise_exception=True)
def product(request):
    return create(request, ProductForm)

@login_required()
@permission_required('core.add_image', raise_exception=True)
def image(request):
    return create(request, ImageForm)
