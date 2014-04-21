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

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse

from iris.core.views.common import create
from iris.packagedb.forms import (DomainForm, SubDomainForm, LicenseForm,
        GitTreeForm, PackageForm, ProductForm, ImageForm)


@login_required()
@permission_required('core.add_domain', raise_exception=True)
def domain(request):
    return create(request, DomainForm, reverse('domain.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('domain.read'), 'Domains'),
                   (None, 'Create'),
                   ))

@login_required()
@permission_required('core.add_subdomain', raise_exception=True)
def subdomain(request):
    return create(request, SubDomainForm, reverse('subdomain.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('subdomain.read'), 'SubDomains'),
                   (None, 'Create'),
                   ))

@login_required()
@permission_required('core.add_license', raise_exception=True)
def license(request):
    return create(request, LicenseForm, reverse('license.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('license.read'), 'Licenses'),
                   (None, 'Create'),
                   ))

@login_required()
@permission_required('core.add_gittree', raise_exception=True)
def gittree(request):
    return create(request, GitTreeForm, reverse('gittree.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('gittree.read'), 'Git trees'),
                   (None, 'Create'),
                  ))

@login_required()
@permission_required('core.add_package', raise_exception=True)
def package(request):
    return create(request, PackageForm, reverse('package.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('package.read'), 'Packages'),
                   (None, 'Create'),
                  ))


@login_required()
@permission_required('core.add_product', raise_exception=True)
def product(request):
    return create(request, ProductForm, reverse('product.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('product.read'), 'Products'),
                   (None, 'Create'),
                  ))


@login_required()
@permission_required('core.add_image', raise_exception=True)
def image(request):
    return create(request, ImageForm, reverse('image.read'),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('image.read'), 'Images'),
                   (None, 'Create'),
                  ))
