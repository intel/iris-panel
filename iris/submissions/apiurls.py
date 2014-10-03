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

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'iris.submissions.views.events',
    url(r'events/(.*?)/', 'events_handler', name='submissions_events'),
    )
