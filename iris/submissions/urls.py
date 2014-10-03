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


#urlpatterns = patterns(
#    'iris.submissions.views.base',
#    url(r'^(?i)$', 'summary', name='summary'),
#    url(r'^group/$', 'create_group', name='create_group'),
#    url(r'^group/create/$', 'create_group_ajax', name='create_group_ajax'),
#)

#urlpatterns += patterns(
#    'iris.submissions.views.create',
#    url(r'^submissiongroups/create/$',
#        'submissiongroups', name='create_submissiongroups'),
#)

urlpatterns = patterns(
    'iris.submissions.views.read',
    url(r'^$', 'index', name='submissions_index'),
    url(r'^mine/$', 'mine', name='my_submissions'),
    url(r'^opened/$', 'opened', name='opened_submissions'),
    url(r'^search/$', 'search', name='search_submissions'),
    url(r'^(.*?)$', 'detail', name='submission_detail'),
)

#urlpatterns += patterns(
#    'iris.submissions.views.update',
#    url(r'^submissions(?:/(?P<pkid>\d+))?/update/$',
#        'submissions', name='update_submissions'),
#    url(r'^submissions(?:/(?P<pkid>\d+))?/accept/$',
#        'accept_submissions', name='accept_submissions'),
#    url(r'^submissions(?:/(?P<pkid>\d+))?/reject/$',
#        'reject_submissions', name='reject_submissions'),
#    url(r'^submissiongroups(?:/(?P<pkid>\d+))?/update/$',
#        'submissiongroups', name='update_submissiongroups'),
#    url(r'^submissiongroups(?:/(?P<pkid>\d+))?/accept/$',
#        'accept_submissiongroups', name='accept_submissiongroups'),
#    url(r'^submissiongroup(?:/(?P<pkid>\d+))?/reject/$',
#        'reject_submissiongroups', name='reject_submissiongroups'),
#)

#urlpatterns += patterns(
#    'iris.submissions.views.delete',
#    url(r'^submissions(?:/(?P<pkid>\d+))?/delete/$',
#        'submissions', name='delete_submissions'),
#    url(r'^submissiongroups(?:/(?P<pkid>\d+))?/delete/$',
#        'submissiongroups', name='delete_submissiongroups'),
#)
