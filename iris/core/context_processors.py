# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
"""
Context processors which accept one argument of HTTPRequest
and return a dict that can be used in all templates.
"""
import pkg_resources

# pylint: disable=E1103
# E1103: version: Instance of 'str' has no 'version' member


def version(_request):
    """
    Returns IRIS version in tuple
    """
    try:
        ver = pkg_resources.get_distribution('iris').version
    except pkg_resources.DistributionNotFound:
        ver = 'dev'
    return {'version': ver}
