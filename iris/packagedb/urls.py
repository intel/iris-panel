# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Main URL configuration for the iris-packagedb project.

Put commonplace URL definitions here.
"""

# pylint: disable=C0103,C0301

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'iris.packagedb.views.base',
    url(r'^(?i)$', 'index', name='packagedb'),
)

urlpatterns += patterns(
    'iris.packagedb.views.create',
    url(r'^subdomains/create/$', 'subdomain', name='subdomain.create'),
    url(r'^domains/create/$', 'domain', name='domain.create'),
    url(r'^licenses/create/$', 'license', name='license.create'),
    url(r'^gittrees/create/$', 'gittree', name='gittree.create'),
    url(r'^packages/create/$', 'package', name='package.create'),
    url(r'^products/create/$', 'product', name='product.create'),
    url(r'^images/create/$', 'image', name='image.create'),
    )

urlpatterns += patterns(
    'iris.packagedb.views.read',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/$',
        'subdomain', name='subdomain.read'),
    url(r'^domains(?:/(?P<pkid>\d+))?/$', 'domain', name='domain.read'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/$', 'license', name='license.read'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/$', 'gittree', name='gittree.read'),
    url(r'^packages(?:/(?P<pkid>\d+))?/$', 'package', name='package.read'),
    url(r'^products(?:/(?P<pkid>\d+))?/$', 'product', name='product.read'),
    url(r'^images(?:/(?P<pkid>\d+))?/$', 'image', name='image.read'),
)

urlpatterns += patterns(
    'iris.packagedb.views.update',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/update/$',
        'subdomain', name='subdomain.update'),
    url(r'^domains(?:/(?P<pkid>\d+))?/update/$',
        'domain', name='domain.update'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/update/$',
        'license', name='license.update'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/update/$',
        'gittree', name='gittree.update'),
    url(r'^packages(?:/(?P<pkid>\d+))?/update/$',
        'package', name='package.update'),
    url(r'^products(?:/(?P<pkid>\d+))?/update/$',
        'product', name='product.update'),
    url(r'^images(?:/(?P<pkid>\d+))?/update/$',
        'image', name='image.update'),
)

urlpatterns += patterns(
    'iris.packagedb.views.delete',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/delete/$',
        'subdomain', name='subdomain.delete'),
    url(r'^domains(?:/(?P<pkid>\d+))?/delete/$',
        'domain', name='domain.delete'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/delete/$',
        'license', name='license.delete'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/delete/$',
        'gittree', name='gittree.delete'),
    url(r'^packages(?:/(?P<pkid>\d+))?/delete/$',
        'package', name='package.delete'),
    url(r'^products(?:/(?P<pkid>\d+))?/delete/$',
        'product', name='product.delete'),
    url(r'^images(?:/(?P<pkid>\d+))?/delete/$',
        'image', name='image.delete'),
)

urlpatterns += patterns(
    'iris.packagedb.views.scm',
    url(r'^scm/update', 'update', name='scm.update'),
    url(r'^scm/check', 'check', name='scm.update'),
)
