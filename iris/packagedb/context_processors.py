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

from iris.core.models import Product


def products(request):
    """ return all products """
    products = Product.objects.all()
    return {'all_products': products}


