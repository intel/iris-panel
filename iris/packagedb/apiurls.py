# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
API URL configuration for the iris-packagedb project.

Permittable URLs and views accessible through REST API are defined here.
"""

# pylint: disable=C0103

from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from iris.packagedb.apiviews import (DomainViewSet, SubDomainViewSet,
    LicenseViewSet, GitTreeViewSet, PackageViewSet, ProductViewSet,
    ImageViewSet)


# Create a router and register our views with it.
router = DefaultRouter()
router.register(r'domains', DomainViewSet)
router.register(r'subdomains', SubDomainViewSet)
router.register(r'licenses', LicenseViewSet)
router.register(r'gittrees', GitTreeViewSet)
router.register(r'packages', PackageViewSet)
router.register(r'products', ProductViewSet)
router.register(r'images', ImageViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.
urlpatterns = patterns(
    'iris.packagedb.apiviews',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
)
