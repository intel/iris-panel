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

from iris.core.views.common import delete
from django.contrib.auth.decorators import login_required, permission_required

from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)


@login_required()
@permission_required('core.delete_domain', raise_exception=True)
def domain(request, pkid):
    return delete(request, pkid, Domain, '/app/packagedb/domains')

@login_required()
@permission_required('core.delete_subdomain', raise_exception=True)
def subdomain(request, pkid):
    domain = request.GET.get('domain')
    return delete(request, pkid, SubDomain,
                  '/app/packagedb/domains/%s/' % (domain,))

@login_required()
@permission_required('core.delete_license', raise_exception=True)
def license(request, pkid):
    return delete(request, pkid, License, '/app/packagedb/licenses')

@login_required()
@permission_required('core.delete_gittree', raise_exception=True)
def gittree(request, pkid):
    return delete(request, pkid, GitTree, '/app/packagedb/gittrees')

@login_required()
@permission_required('core.delete_package', raise_exception=True)
def package(request, pkid):
    return delete(request, pkid, Package, '/app/packagedb/packages')

@login_required()
@permission_required('core.delete_product', raise_exception=True)
def product(request, pkid):
    return delete(request, pkid, Product, '/app/packagedb/products')

@login_required()
@permission_required('core.delete_image', raise_exception=True)
def image(request, pkid):
    return delete(request, pkid, Image, '/app/packagedb/images')
