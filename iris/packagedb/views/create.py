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
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from iris.core.permissions import (can_create_products,
        can_create_domains, can_create_subdomains, can_create_gittrees,
        can_create_packages, can_create_licenses, can_create_images)
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
def domain(request):
    if not can_create_domains(request.user):
        raise PermissionDenied()

    return create(request, DomainForm)

@login_required()
def subdomain(request):
    if not can_create_subdomains(request.user):
        raise PermissionDenied()

    return create(request, SubDomainForm)

@login_required()
def license(request):
    if not can_create_licenses(request.user):
        raise PermissionDenied()

    return create(request, LicenseForm)

@login_required()
def gittree(request):
    if not can_create_gittrees(request.user):
        raise PermissionDenied()

    return create(request, GitTreeForm)

@login_required()
def package(request):
    if not can_create_packages(request.user):
        raise PermissionDenied()

    return create(request, PackageForm)

@login_required()
def product(request):
    if not can_create_products(request.user):
        raise PermissionDenied()

    return create(request, ProductForm)

@login_required()
def image(request):
    if not can_create_images(request.user):
        raise PermissionDenied()

    return create(request, ImageForm)
