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

from rest_framework.viewsets import ModelViewSet
from rest_framework.status import HTTP_406_NOT_ACCEPTABLE
from rest_framework.response import Response

from iris.core.models import Submission, Product
from iris.submissions.serializers import SubmissionSerializer

class SubmissionViewSet(ModelViewSet):

    # pylint: disable=E1101,R0901,R0904

    """
    View to the submissions provided by the API.
    """

    model = Submission
    serializer_class = SubmissionSerializer

    def get_queryset(self):
        return Submission.objects.all()

    def list(self, request):
        """List submissions."""
        queryset = self.get_queryset()
        name = request.GET.get('name')
        if name:
            queryset = queryset.filter(name__iexact=name)

        product = request.GET.get('product')
        if product:
            try:
                prodobj = Product.objects.get(short=product)
            except Product.DoesNotExist:
                return Response({'error': "Product %s doesn't exist" % product},
                                status=HTTP_406_NOT_ACCEPTABLE)
            queryset = queryset.filter(product=prodobj)

        active = request.GET.get('active')
        status = request.GET.get('status')
        if active and status:
            return Response(
                    {'error': "Status and active can't be used together"},
                    status=HTTP_406_NOT_ACCEPTABLE)
        if status:
            statuses = [stat.upper() for stat, _descr \
                           in Submission.SUBMISSIONSTATUS]
            if status.upper() not in statuses:
                return Response({'error': 'Incorrect status value'},
                       status=HTTP_406_NOT_ACCEPTABLE)
            queryset = queryset.filter(status__iexact=status)

        elif active:
            if active not in ('0', '1'):
                return Response({'error': "Incorrect value of 'active'"},
                                 status=HTTP_406_NOT_ACCEPTABLE)
            if active == '1':
                queryset = queryset.exclude(status__in=['ACCEPTED', 'REJECTED'])
            else:
                queryset = queryset.filter(status__in=['ACCEPTED', 'REJECTED'])

        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

