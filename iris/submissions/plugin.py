# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This file contains the relevant data for the iris-submissions so the
entry point plugin system can load this Django application on startup.

Information of entry points is supplied in the APPINFO dictionary,
which provides fields:
    header
        for the application brief name
    name
        name as in the application's containing package / directoryname
    template_dirs
        Django template directories for accessing application templates
    urlpatterns
        for API and web UI access
    installed_apps
        a iterable containing this application's name for adding to Django core
    intro
        introductionary message of this app for the frontpage

Private variables for constructing the app entry point are
prefixed with a lodash (e.g. _NAME) and are to be used inside this module.
"""

from os.path import join, dirname, abspath, basename


_HEADER = 'Submissions'
_NAME = basename(dirname(abspath(__file__)))
print _NAME
# print basename(dirname(abspath(__file__)))

_INSTALLED_APPS = (
    'iris.%s' % _NAME,
)

_TEMPLATE_DIRS = (
    abspath(join(dirname(__file__), 'templates')),
)

_URLPATTERNS = {
    'baseurl': r'^app/%s/' % _NAME,
    'patterns': 'iris.%s.urls' % _NAME,
}

_INTRO = """IRIS Submissions. Contains metadata about
CI and build system statuses and package integration."""

APPINFO = {
    'header': _HEADER,
    'name': _NAME,
    'template_dirs': _TEMPLATE_DIRS,
    'urlpatterns': _URLPATTERNS,
    'installed_apps': _INSTALLED_APPS,
    'intro': _INTRO,
}
