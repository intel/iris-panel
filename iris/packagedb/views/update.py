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

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from iris.core.permissions import can_edit
from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)
from iris.packagedb.forms import (DomainForm, SubDomainForm, LicenseForm,
        GitTreeForm, PackageForm, ProductForm, ImageForm)


def update(request, pkid, model, form):
    """
    A generic wrapper for updating given objects with a form.

    For GET renders a prefilled form, for POST validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with GET or PUT
    :param  pkid:       Django model object database ID to fetch
    :type   pkid:       integer
    :param  model:      Django model class to use for request
    :type   model:      Django model class
    :param  form:       Django form class to use for request
    :type   form:       Django form class

    Example usage::

        def example(request):
            return update(request, pkid, ExampleModel, ExampleForm)

    Which would use
    Exampleform to instanciate a form,
    Examplemodel and pkid to fetch the object to use for the update operation,
    """

    obj = get_object_or_404(model, id=pkid) if pkid else None

    if not can_edit(request.user, obj):
        raise PermissionDenied()

    form = form(request.POST or None, instance=obj)
    url = None

    if request.POST and form.is_valid():
        form.save()
        url = '%s/' % request.path.rstrip('update/')
        messages.success(request, 'Update successful!')

    return render(request, 'packagedb/update.html', {
        'form': form,
        'url': url})


@login_required
def domain(request, pkid):
    return update(request, pkid, Domain, DomainForm)

@login_required
def subdomain(request, pkid):
    return update(request, pkid, SubDomain, SubDomainForm)

@login_required
def license(request, pkid):
    return update(request, pkid, License, LicenseForm)

@login_required
def gittree(request, pkid):
    return update(request, pkid, GitTree, GitTreeForm)

@login_required
def package(request, pkid):
    return update(request, pkid, Package, PackageForm)

@login_required
def product(request, pkid):
    return update(request, pkid, Product, ProductForm)

@login_required
def image(request, pkid):
    return update(request, pkid, Image, ImageForm)
