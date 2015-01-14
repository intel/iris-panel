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

# pylint: disable=E1101,W0232,C0111,R0901,R0904,W0613
#W0613: Unused argument %r(here it is request)

from rest_framework.viewsets import ReadOnlyModelViewSet, ViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from iris.core.models import (SubDomain, GitTree, Package, Product)
from iris.packagedb.serializers import (
    DomainSerializer, GitTreeSerializer, PackageSerializer, ProductSerializer)


class DomainViewSet(ViewSet):
    """
    View to the Domains provided by the API.
    """

    def list(self, request):
        queryset = SubDomain.objects.prefetch_related(
            'domain__role_set__user_set',
            'subdomainrole_set__user_set')
        serializer = DomainSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, name=None):
        domain, subdomain = name.split('/')
        obj = get_object_or_404(SubDomain,
                                name=subdomain.strip(),
                                domain__name=domain.strip())
        serializer = DomainSerializer(obj)
        return Response(serializer.data)


class GitTreeViewSet(ReadOnlyModelViewSet):
    """
    View to the GitTrees provided by the API.
    """

    queryset = GitTree.objects.select_related(
        'subdomain__domain',
        ).prefetch_related(
            'packages',
            'licenses',
            'role_set__user_set'
        ).all()
    serializer_class = GitTreeSerializer
    lookup_field = 'gitpath'


class PackageViewSet(ReadOnlyModelViewSet):
    """
    View to the Packages provided by the API.
    """

    queryset = Package.objects.prefetch_related('gittree_set').all()
    serializer_class = PackageSerializer
    lookup_field = 'name'


class ProductViewSet(ReadOnlyModelViewSet):
    """
    View to the Products provided by the API.
    """

    queryset = Product.objects.prefetch_related('gittrees').all()
    serializer_class = ProductSerializer
    lookup_field = 'name'
