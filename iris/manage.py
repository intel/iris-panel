# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the management module for the iris-core project.
"""

from os.path import abspath, join, dirname
from os import environ
from sys import argv, path

if __name__ == "__main__":
    PROJECT_ROOT = abspath(join(dirname(__file__), '..'))

    if PROJECT_ROOT not in path:
        path.insert(0, PROJECT_ROOT)

    environ.setdefault("DJANGO_SETTINGS_MODULE", "iris.core.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(argv)
