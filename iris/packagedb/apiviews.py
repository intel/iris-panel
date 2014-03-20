# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the API view file for the iris-packagedb application.

Views shown by REST Framework under API URLs are defined here.
"""

# pylint: disable=E1101,W0232,C0111,R0901,R0904

from rest_framework.viewsets import ReadOnlyModelViewSet


from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
    Product, Image)
from iris.packagedb.serializers import (DomainSerializer, SubDomainSerializer,
    LicenseSerializer, GitTreeSerializer, PackageSerializer, ProductSerializer,
    ImageSerializer)



class DomainViewSet(ReadOnlyModelViewSet):
    """
    View to the Domains provided by the API.
    """

    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class SubDomainViewSet(ReadOnlyModelViewSet):
    """
    View to the SubDomains provided by the API.
    """

    queryset = SubDomain.objects.all()
    serializer_class = SubDomainSerializer


class LicenseViewSet(ReadOnlyModelViewSet):
    """
    View to the Licenses provided by the API.
    """

    queryset = License.objects.all()
    serializer_class = LicenseSerializer


class GitTreeViewSet(ReadOnlyModelViewSet):
    """
    View to the GitTrees provided by the API.
    """

    queryset = GitTree.objects.all()
    serializer_class = GitTreeSerializer


class PackageViewSet(ReadOnlyModelViewSet):
    """
    View to the Packages provided by the API.
    """

    queryset = Package.objects.all()
    serializer_class = PackageSerializer


class ProductViewSet(ReadOnlyModelViewSet):
    """
    View to the Products provided by the API.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ImageViewSet(ReadOnlyModelViewSet):
    """
    View to the Images provided by the API.
    """

    queryset = Image.objects.all()
    serializer_class = ImageSerializer
