# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Main URL configuration for the iris-submissions project.

Put commonplace URL definitions here.
"""

# pylint: disable=C0103

from django.conf.urls import patterns, url


urlpatterns = patterns(
    'iris.submissions.views.base',
    url(r'^(?i)$', 'index', name='index'),
    url(r'^summary/$', 'summary', name='summary'),
)
