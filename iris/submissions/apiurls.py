# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.1 as published by the Free Software Foundation.

"""
API URL configuration for the iris-submissions project.

Permittable URLs and views accessible through REST API are defined here.
"""

# pylint: disable=C0103

from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter

from iris.submissions.apiviews import SubmissionViewSet

# Create a router and register our views with it.
router = DefaultRouter()
router.register(r'items', SubmissionViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browseable API.

urlpatterns = patterns(
    'iris.submissions.apiviews',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
)


urlpatterns += patterns(
    'iris.submissions.views.events',
    url(r'events/submitted/', 'submitted', name='event_submitted'),
    url(r'events/pre_created/', 'pre_created', name='event_pre_created'),
    url(r'events/image_building/', 'image_building',
        name='event_image_building'),
    url(r'events/image_created/', 'image_created', name='event_image_created'),
    )
