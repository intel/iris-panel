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
    url(r'^(?i)$', 'index', name='index'),
)

urlpatterns += patterns(
    'iris.packagedb.views.create',
    url(r'^subdomains/create/$', 'subdomain', name='subdomain'),
    url(r'^domains/create/$', 'domain', name='domain'),
    url(r'^licenses/create/$', 'license', name='license'),
    url(r'^gittrees/create/$', 'gittree', name='gittree'),
    url(r'^packages/create/$', 'package', name='package'),
    url(r'^products/create/$', 'product', name='product'),
    url(r'^images/create/$', 'image', name='image'),
    )

urlpatterns += patterns(
    'iris.packagedb.views.read',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/$', 'subdomain', name='subdomain'),
    url(r'^domains(?:/(?P<pkid>\d+))?/$', 'domain', name='domain'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/$', 'license', name='license'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/$', 'gittree', name='gittree'),
    url(r'^packages(?:/(?P<pkid>\d+))?/$', 'package', name='package'),
    url(r'^products(?:/(?P<pkid>\d+))?/$', 'product', name='product'),
    url(r'^images(?:/(?P<pkid>\d+))?/$', 'image', name='image'),
)

urlpatterns += patterns(
    'iris.packagedb.views.update',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/update/$',
        'subdomain', name='subdomain'),
    url(r'^domains(?:/(?P<pkid>\d+))?/update/$', 'domain', name='domain'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/update/$', 'license', name='license'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/update/$', 'gittree', name='gittree'),
    url(r'^packages(?:/(?P<pkid>\d+))?/update/$', 'package', name='package'),
    url(r'^products(?:/(?P<pkid>\d+))?/update/$', 'product', name='product'),
    url(r'^images(?:/(?P<pkid>\d+))?/update/$', 'image', name='image'),
)

urlpatterns += patterns(
    'iris.packagedb.views.delete',
    url(r'^subdomains(?:/(?P<pkid>\d+))?/delete/$',
        'subdomain', name='subdomain'),
    url(r'^domains(?:/(?P<pkid>\d+))?/delete/$', 'domain', name='domain'),
    url(r'^licenses(?:/(?P<pkid>\d+))?/delete/$', 'license', name='license'),
    url(r'^gittrees(?:/(?P<pkid>\d+))?/delete/$', 'gittree', name='gittree'),
    url(r'^packages(?:/(?P<pkid>\d+))?/delete/$', 'package', name='package'),
    url(r'^products(?:/(?P<pkid>\d+))?/delete/$', 'product', name='product'),
    url(r'^images(?:/(?P<pkid>\d+))?/delete/$', 'image', name='image'),
)
