# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the serializer file for the iris-packagedb application.

Permittable fields and serializer validation behaviour is defined here.
"""

# pylint: disable=W0232,C0111,R0903

from rest_framework.serializers import ModelSerializer

from iris.core.models import (Domain, SubDomain, License, GitTree,
        Package, Product, Image)


class DomainSerializer(ModelSerializer):
    """
    Serializer class for the Domain model.
    """

    class Meta:
        model = Domain
        fields = ('name',)


class SubDomainSerializer(ModelSerializer):
    """
    Serializer class for the SubDomain model.
    """

    class Meta:
        model = SubDomain
        fields = ('name', 'domain')


class LicenseSerializer(ModelSerializer):
    """
    Serializer class for the License model.
    """

    class Meta:
        model = License
        fields = ('shortname', 'text', 'url', 'fullname', 'notes',
                  'active', 'text_updatable', 'md5', 'detector_type')


class GitTreeSerializer(ModelSerializer):
    """
    Serializer class for the GitTree model.
    """

    class Meta:
        model = GitTree
        fields = ('gitpath', 'subdomain', 'licenses')


class PackageSerializer(ModelSerializer):
    """
    Serializer for the Package model.
    """

    class Meta:
        model = Package
        fields = ('name', 'gittree')


class ProductSerializer(ModelSerializer):
    """
    Serializer class for the Product model.
    """

    class Meta:
        model = Product
        fields = ('name', 'short', 'state', 'targets', 'gittrees')


class ImageSerializer(ModelSerializer):
    """
    Serializer class for the Image model.
    """

    class Meta:
        model = Image
        fields = ('name', 'target', 'arch', 'product')
