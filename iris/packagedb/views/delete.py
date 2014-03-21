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

from django.shortcuts import render, get_object_or_404
from django.forms.models import model_to_dict
from django.contrib.auth.decorators import login_required, permission_required
from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)


def delete(request, pkid, model):
    """
    A generic wrapper for deleting objects of type Model with id pkid.

    For GET renders an empty form, for PUT validates and saves the form.

    :param  request:    Django HTTP request context to handle
    :type   request:    Django HTTP request object with DELETE
    :param  pkid:       Django model object database ID to fetch
    :type   pkid:       integer
    :param  model:      Django model class to use for request
    :type   model:      Django model class

    Example usage::

        def example(request):
            return delete(request, pkid, ExampleModel)
    """

    obj = get_object_or_404(model, id=pkid)
    deleted = model_to_dict(obj)
    obj.delete()

    return render(request, 'packagedb/delete.html', {'deleted': deleted})


@login_required()
@permission_required('core.delete_domain', raise_exception=True)
def domain(request, pkid):
    return delete(request, pkid, Domain)

@login_required()
@permission_required('core.delete_subdomain', raise_exception=True)
def subdomain(request, pkid):
    return delete(request, pkid, SubDomain)

@login_required()
@permission_required('core.delete_license', raise_exception=True)
def license(request, pkid):
    return delete(request, pkid, License)

@login_required()
@permission_required('core.delete_gittree', raise_exception=True)
def gittree(request, pkid):
    return delete(request, pkid, GitTree)

@login_required()
@permission_required('core.delete_package', raise_exception=True)
def package(request, pkid):
    return delete(request, pkid, Package)

@login_required()
@permission_required('core.delete_product', raise_exception=True)
def product(request, pkid):
    return delete(request, pkid, Product)

@login_required()
@permission_required('core.delete_image', raise_exception=True)
def image(request, pkid):
    return delete(request, pkid, Image)
