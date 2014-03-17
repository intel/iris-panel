# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the read view file for the iris-packagedb application.

Views for listing single and multiple item info is contained here.
"""

# pylint: disable=C0111,W0622

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)
from iris.core.models import ProductRole, UserParty
from iris.packagedb.injectors import (inject_domain, inject_subdomain,
        inject_gittree, inject_product)


@login_required()
def domain(request, pkid=None):
    if pkid:
        _domain = inject_domain(get_object_or_404(Domain, id=pkid))
        return render(request, 'packagedb/read/single/domain.html',
                {'domain': _domain})
    else:
        return render(request, 'packagedb/read/multiple/domains.html',
                {'domains': Domain.objects.all()})

@login_required()
def subdomain(request, pkid=None):
    if pkid:
        _subdomain = inject_subdomain(get_object_or_404(SubDomain, id=pkid))
        return render(request, 'packagedb/read/single/subdomain.html',
                {'subdomain': _subdomain})
    else:
        _subdomains = [inject_subdomain(d) for d in SubDomain.objects.all()]
        return render(request, 'packagedb/read/multiple/subdomains.html',
                {'subdomains': _subdomains})

@login_required()
def license(request, pkid=None):
    if pkid:
        _license = get_object_or_404(License, id=pkid)
        _packages = [p for g in _license.gittree_set.all()
                      for p in g.package_set.all()]
        return render(request, 'packagedb/read/single/license.html',
                {'license': _license,
                 'packages': _packages})
    else:
        return render(request, 'packagedb/read/multiple/licenses.html',
                {'licenses': License.objects.all()})

@login_required()
def gittree(request, pkid=None):
    if pkid:
        _gittree = inject_gittree(get_object_or_404(GitTree, id=pkid))
        return render(request, 'packagedb/read/single/gittree.html',
                {'gittree': _gittree})
    else:
        _gittrees = [inject_gittree(g) for g in GitTree.objects.all()]
        return render(request, 'packagedb/read/multiple/gittrees.html',
                {'gittrees': _gittrees})

@login_required()
def package(request, pkid=None):
    if pkid:
        return render(request, 'packagedb/read/single/package.html',
                {'package': get_object_or_404(Package, id=pkid)})
    else:
        return render(request, 'packagedb/read/multiple/packages.html',
                {'packages': Package.objects.all()})

@login_required()
def product(request, pkid=None):
    if pkid:
        _product = inject_product(get_object_or_404(Product, id=pkid))
        return render(request, 'packagedb/read/single/product.html',
                {'product': _product})
    else:
        _products = [inject_product(p) for p in Product.objects.all()]
        return render(request, 'packagedb/read/multiple/products.html',
                {'products': _products})

@login_required()
def image(request, pkid=None):
    if pkid:
        return render(request, 'packagedb/read/single/image.html',
                {'image': get_object_or_404(Image, id=pkid)})
    else:
        return render(request, 'packagedb/read/multiple/images.html',
                {'images': Image.objects.all()})
