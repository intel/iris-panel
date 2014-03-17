# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

# pylint: disable=C0103

"""
WSGI config for iris-core project.
"""

import sys
from os import path, environ
from iris import core

PROJECT_PATH = path.abspath(path.dirname(path.dirname(core.__file__)))

if not PROJECT_PATH in sys.path:
    sys.path.append(PROJECT_PATH)

environ.setdefault("DJANGO_SETTINGS_MODULE", "iris.core.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
