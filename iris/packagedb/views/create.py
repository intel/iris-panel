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

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from iris.packagedb.forms import (DomainForm, SubDomainForm, LicenseForm,
        GitTreeForm, PackageForm, ProductForm, ImageForm)


def create(request, form):
    """
    A generic wrapper for creating given objects from a form.

    For GET renders an empty form, for POST validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with GET or POST
    :param  form:       Django form class to use for request
    :param  form:       Django form class

    Example usage::

        def create_example(request):
            return create(request, ExampleForm)

    Which would use ExampleForm to instanciate a form and save possible object.
    """

    form = form(request.POST or None)
    url = None

    if request.method == 'POST' and form.is_valid():
        created = form.save()
        url = '%s/%s/' % (request.path.rstrip('create/'), created.id)
        messages.success(request, 'Creation successful!')

    return render(request, 'packagedb/create.html', {
        'form': form,
        'url': url})

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
