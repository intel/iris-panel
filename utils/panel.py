# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
Tool to log sql queries info for debugging purpose, implemented by subclassing
django debug toolbar's SQLPanel, make sure you've installed debug_toolbar
before using it.

An example of configuration is listed below:

1. Add LogSQLPanel to DEBUG_TOOLBAR_PANELS in your django settings file.

DEBUG_TOOLBAR_PANELS = [
    'yourmodule.panel.LogSQLPanel' #importable module path of LogSQLPanel
]

2. LogSQLPanel will log DEBUG level message, configure LOGGING in django settings file,
add loggers and handlers if needed.

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'verbose': {
            'format': '[%(levelname)s] %(asctime)s|%(name)s|%(message)s',
        }
    },
    'handlers': {
        'sql_debug':{
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.FileHandler',
            'filename': 'yourpath/sql.log',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'yourmodule.panel': {
            'handlers': ['sql_debug'],
            'level': 'DEBUG',
        }
    }
}

3. If the debug toolbar doesn't show up on the web page, you can check to see
whether your ip is in internal ips, you may either set INTERNAL_IPS or forbid
ip checks by using SHOW_TOOLBAR_CALLBACK, see
https://django-debug-toolbar.readthedocs.org/en/latest/installation.html#internal-ips
for more information.
"""

import logging
from debug_toolbar.panels.sql.panel import SQLPanel

# pylint: disable=invalid-name
# C: 15, 0: Invalid constant name "logger" (invalid-name)

logger = logging.getLogger(__name__)

class LogSQLPanel(SQLPanel):
    """
    Panel that log information of sql queries
    by subclassing debug toolbar's SQLPanel.
    """

    def process_response(self, request, response):
        """
        Log url and number of sql queries.
        """
        super(LogSQLPanel, self).process_response(request, response)
        logger.debug('%s %s %s' % (request.get_full_path(), self._num_queries, self._sql_time))
