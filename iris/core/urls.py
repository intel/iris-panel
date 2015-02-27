# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Main URL configuration for the iris-core project.

Put commonplace URL definitions here.
"""

# Disable Django specific 'urlpatterns' name flagging
# pylint: disable=C0103

from logging import getLogger
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
)

urlpatterns += patterns(
    'iris.core.views.base',
    url(r'^$', 'index', name='index'),
    url(r'^404/$', 'error', name='error'),
    url(r'^login/$', 'login_view', name='login_view'),
    url(r'^logout/$', 'logout_view', name='logout_view'),
    url(r'^settings/$', 'settings_view', name='settings_view'),
    url(r'^users(?:/(?P<pkid>\d+))?/$', 'users', name='users'),
)

urlpatterns += patterns(
    '',
    url(r'^app/packagedb/', include('iris.packagedb.urls')),
    url(r'^api/packagedb/', include('iris.packagedb.apiurls')),
    url(r'^app/submissions/', include('iris.submissions.urls')),
    url(r'^api/submissions/', include('iris.submissions.apiurls')),
)

LOGGER = getLogger('iris')

if settings.REST_API_AVAILABLE:
    urlpatterns += patterns(
        '',
        url(r'^api/doc/', include('rest_framework_swagger.urls')),
    )

    LOGGER.info('Loaded REST API documentation under /api/doc')
