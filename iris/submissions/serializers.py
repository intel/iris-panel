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

from rest_framework.serializers import ModelSerializer

from iris.core.models import Submission


class SubmissionSerializer(ModelSerializer):
    """
    Serializer class for the Submission model.
    """

    class Meta:
        model = Submission
        fields = ('name', 'commit', 'status')

