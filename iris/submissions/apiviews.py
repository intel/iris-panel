# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.1 as published by the Free Software Foundation.

"""
This is the API view file for the iris-submissions application.

Views shown by REST Framework under API URLs are defined here.
"""

# pylint: disable=W0232,C0111,R0901,R0904

from rest_framework.viewsets import ReadOnlyModelViewSet


from iris.core.models import Submission
from iris.submissions.serializers import SubmissionSerializer


class SubmissionViewSet(ReadOnlyModelViewSet):
    """
    View to the submissions provided by the API.
    """

    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer

