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
    'iris.submissions.views.read',
    url(r'^$', 'index', name='submissions_index'),
    url(r'^mine/$', 'mine', name='my_submissions'),
    url(r'^snapshots/(?P<pkid>\d+)/$', 'snapshot', name='snapshot_detail'),
    url(r'^snapshots/product/(?P<product_id>\d+)/$', 'snapshot_by_product', name='snapshot_by_product'),
    url(r'^snapshots/product/(?P<product_id>\d+)/(?P<offset>\d+)/(?P<limit>\d+)/$', 'snapshot_by_product', name='snapshot_by_offset_limit'),
    url(r'^opened/$', 'opened', name='opened_submissions'),
    url(r'^accepted/$', 'accepted', name='accepted_submissions'),
    url(r'^rejected/$', 'rejected', name='rejected_submissions'),
    url(r'^search/$', 'search', name='search_submissions'),
    url(r'^(.*?)$', 'detail', name='submission_detail'),
)
