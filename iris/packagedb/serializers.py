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

from rest_framework.serializers import (
    ModelSerializer, RelatedField, SlugRelatedField, Serializer, CharField)

from iris.core.models import (GitTree, Package, Product, role_users)


class DomainField(RelatedField):
    """ Refine subdomain name when display"""

    def to_native(self, value):
        return value.fullname


class RoleSetField(RelatedField):
    """ Refine roleset GitTree """

    def to_native(self, value):
        return role_users(value.all(), 'first_name', 'last_name', 'email')


class DomainSerializer(Serializer):
    """ Serializer class for the Domain model. """

    name = CharField(max_length=200)
    roles = CharField(max_length=512)

    def to_native(self, obj):
        if obj.name.lower() == 'uncategorized':
            # get roles by domain
            ins = obj.domain
        else:
            # get roles by subdomain
            ins = obj
        return {'name': obj.fullname,
                'roles': ins.roles('first_name', 'last_name', 'email')}


class GitTreeSerializer(ModelSerializer):
    """
    Serializer class for the GitTree model.
    """

    domain = DomainField(source='subdomain')
    licenses = SlugRelatedField(many=True, slug_field='shortname')
    packages = RelatedField(many=True)
    roles = RoleSetField(source='role_set')

    class Meta:
        model = GitTree
        fields = ('gitpath', 'domain', 'roles', 'packages', 'licenses')


class PackageSerializer(ModelSerializer):
    """
    Serializer for the Package model.
    """

    gittrees = RelatedField(source='gittree_set', many=True)

    class Meta:
        model = Package
        fields = ('name', 'gittrees')


class ProductSerializer(ModelSerializer):
    """
    Serializer class for the Product model.
    """

    gittrees = RelatedField(many=True)

    class Meta:
        model = Product
        fields = ('name', 'description', 'gittrees')
