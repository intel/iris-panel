# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
API URL configuration for the iris-submissions project.

Permittable URLs and views accessible through REST API are defined here.
"""

# pylint: disable=C0103

from django.conf.urls import patterns, url, include

urlpatterns = patterns(
    'iris.submissions.views.events',
    url(r'events/(.*?)/', 'events_handler', name='submissions_events'),
    )

urlpatterns += patterns(
    'iris.submissions.apiviews',
    url(r'^(?P<project>[\w:]+)/$', 'list_submissions_by_product', name='submissions_list_by_product'),
    url(r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')),
)
