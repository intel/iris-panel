# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.1 as published by the Free Software Foundation.

"""
This is the serializer file for the iris-submissions application.

Permittable fields and serializer validation behaviour is defined here.
"""

# pylint: disable=W0232,C0111,R0903

from rest_framework import serializers

from iris.core.models import Submission, SubmissionGroup


class SubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Submission model.
    """

    product = serializers.SlugRelatedField(slug_field='short')
    gittree = serializers.SlugRelatedField(many=True, slug_field='gitpath')
    submitters = serializers.SlugRelatedField(many=True, slug_field='email')

    class Meta:
        model = Submission
        fields = ('id', 'name', 'gittree', 'product', 'commit', 'status',
                  'submitters', 'comment')

class SubmissionGroupSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Submission model.
    """

    class Meta:
        model = SubmissionGroup
        fields = ('name', 'author', 'product', 'submissions', 'status')

