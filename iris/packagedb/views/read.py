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

# pylint: disable=E1101,C0111,W0622

from django.shortcuts import render, get_object_or_404
from django.conf import settings

from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
        Product, Image)
from iris.packagedb.injectors import (inject_domain, inject_subdomain,
        inject_gittree)


def domain(request, pkid=None):
    if pkid:
        _domain = inject_domain(get_object_or_404(Domain, id=pkid))
        return render(request, 'packagedb/read/single/domain.html',
                      {'domain': _domain})
    res = Domain.objects.all().prefetch_related(
        'subdomain_set', 'role_set', 'role_set__user_set')
    return render(request, 'packagedb/read/multiple/domains.html',
                  {'domains': res})


def subdomain(request, pkid=None):
    if pkid:
        _subdomain = inject_subdomain(get_object_or_404(SubDomain, id=pkid))
        return render(request, 'packagedb/read/single/subdomain.html',
                {'subdomain': _subdomain})
    else:
        _subdomains = [inject_subdomain(d) for d in SubDomain.objects.all()]
        return render(request, 'packagedb/read/multiple/subdomains.html',
                {'subdomains': _subdomains})


def license(request, pkid=None):
    if pkid:
        _license = get_object_or_404(License, id=pkid)
        _packages = [p for g in _license.gittree_set.all()
                      for p in g.packages.all()]
        return render(request, 'packagedb/read/single/license.html',
                {'license': _license,
                 'packages': _packages})
    else:
        return render(request, 'packagedb/read/multiple/licenses.html',
                {'licenses': License.objects.all()})


def gittree(request, pkid=None):
    if pkid:
        _gittree = inject_gittree(get_object_or_404(GitTree, id=pkid))
        return render(request, 'packagedb/read/single/gittree.html',
                {'gittree': _gittree})
    else:
        _gittrees = GitTree.objects.select_related(
            'subdomain', 'subdomain__domain'
            ).all().prefetch_related(
            'role_set', 'role_set__user_set')
        return render(request, 'packagedb/read/multiple/gittrees.html', {
            'gittrees': _gittrees,
            'cache_seconds': settings.CACHE_MIDDLEWARE_SECONDS,
        })


def package(request, pkid=None):
    if pkid:
        return render(request, 'packagedb/read/single/package.html',
                {'package': get_object_or_404(Package, id=pkid)})
    else:
        subdomains = SubDomain.objects.select_related(
                        'domain'
                    ).prefetch_related('gittree_set__packages')
        return render(request, 'packagedb/read/multiple/packages.html', {
            'subdomains': subdomains,
            'cache_seconds': settings.CACHE_MIDDLEWARE_SECONDS,
        })


def product(request, pkid=None):
    if pkid:
        _product = get_object_or_404(Product, id=pkid)
        trees = _product.gittrees.select_related(
            'subdomain', 'subdomain__domain').all()
        return render(request, 'packagedb/read/single/product.html',
                {'product': _product, 'gittrees': trees})
    else:
        products = Product.objects.all()
        return render(request, 'packagedb/read/multiple/products.html',
                      {'products': products})


def image(request, pkid=None):
    if pkid:
        return render(request, 'packagedb/read/single/image.html',
                {'image': get_object_or_404(Image, id=pkid)})
    else:
        return render(request, 'packagedb/read/multiple/images.html',
                {'images': Image.objects.select_related('product').all()})
