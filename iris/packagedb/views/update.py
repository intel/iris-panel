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

from iris.core.views.common import update
from iris.core.models import (Domain, SubDomain,
        License, GitTree, Package, Product, Image)
from iris.packagedb.forms import (DomainForm, SubDomainForm,
        LicenseForm, GitTreeForm, PackageForm, ProductForm, ImageForm)


@login_required
@permission_required('core.change_domain', raise_exception=True)
def domain(request, pkid):
    return update(request, pkid, Domain, DomainForm,
                  reverse('domain.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('domain.read'), 'Domains'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_subdomain', raise_exception=True)
def subdomain(request, pkid):
    return update(request, pkid, SubDomain, SubDomainForm,
                  reverse('subdomain.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('subdomain.read'), 'SubDomains'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_license', raise_exception=True)
def license(request, pkid):
    return update(request, pkid, License, LicenseForm,
                  reverse('license.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('license.read'), 'Licenses'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_gittree', raise_exception=True)
def gittree(request, pkid):
    return update(request, pkid, GitTree, GitTreeForm,
                  reverse('gittree.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('gittree.read'), 'Git trees'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_package', raise_exception=True)
def package(request, pkid):
    return update(request, pkid, Package, PackageForm,
                  reverse('package.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('package.read'), 'Packages'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_product', raise_exception=True)
def product(request, pkid):
    return update(request, pkid, Product, ProductForm,
                  reverse('product.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('product.read'), 'Products'),
                   (None, "Update"),
                   ))


@login_required
@permission_required('core.change_image', raise_exception=True)
def image(request, pkid):
    return update(request, pkid, Image, ImageForm,
                  reverse('image.read', args=(pkid,)),
                  (('/', 'IRIS'),
                   (reverse('packagedb'), 'Package Database'),
                   (reverse('image.read'), 'Images'),
                   (None, "Update"),
                   ))
