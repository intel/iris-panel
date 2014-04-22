# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the REST framework test class for the iris-submissions project REST API.
"""

# pylint: disable=E1101,E1103,R0904,C0103

import base64
from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.status import (HTTP_200_OK, HTTP_404_NOT_FOUND,
                                   HTTP_406_NOT_ACCEPTABLE, HTTP_201_CREATED,
                                   HTTP_400_BAD_REQUEST)

from iris.core.models import Product, Submission


def basic_auth_header(username, password):
    """
    Build basic authorization header
    """
    credentials = '%s:%s' % (username, password)
    base64_credentials = base64.b64encode(credentials)
    return 'Basic %s' % base64_credentials


class AuthTests(TestCase):
    """
    The REST framework test case class of Authorization
    """

    def setUp(self):
        """
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')


    def test_auth_fail(self):
        """
        Get requests to APIView should raise 403
        if dose not sign in.
        """

        url = '/api/submissions/items/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data,
            {u'detail': u'Authentication credentials were not provided.'})


    def test_auth_success(self):
        """
        Login success should return True.
        """
        url = '/api/submissions/items/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertTrue(response)


class SubmissionsTests(TestCase):
    """
    The REST framework test case class of Submissions APIView
    """

    def setUp(self):
        """
        Create 1 Submission instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        product = Product.objects.create(name='prod', description='Product')

        self.fixture_obj = Submission.objects.create(
                               name='submit/product/20140321.223750',
                               commit='2ae265f9820cb36e',
                               status='SUBMITTED', product=product)

        self.data = [{'id': obj.id, 'name': obj.name, 'commit': obj.commit,
                      'product': obj.product.name, 'status': obj.status,
                      'comment': obj.comment,
                      'gittree': [item for item in obj.gittree.all()],
                      'submitters': [item for item in obj.submitters.all()],
                     } for obj in Submission.objects.all()]


    def test_get_full_list(self):
        """
        GET full list of submissions
        """

        url = '/api/submissions/items/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_query_by_name(self):
        """
         GET submissions by name.
        """
        url = '/api/submissions/items/?name=submit/product/20140321.223750'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_empty_query_by_name(self):
        """"
        GET empty results by querying by non-existing name
        """
        url = '/api/submissions/items/?name=this_submission_doesnt_exist'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_query_by_product(self):
        """
        GET submissions by product
        """
        url = '/api/submissions/items/?product=prod'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_failed_query_by_product(self):
        """
        Test failed query by querying non-existing product
        """
        url = '/api/submissions/items/?product=this_product_doesnt_exist'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def test_query_by_status(self):
        """
        GET submissions by status
        """
        url = '/api/submissions/items/?status=SUBMITTED'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_failed_query_by_status(self):
        """
        Test failed query by querying non-existing status
        """
        url = '/api/submissions/items/?status=this_status_doesnt_exist'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def test_case_insensitive_status(self):
        """
        Test that status can be case insensitive
        """
        url = '/api/submissions/items/?status=SuBmiTTeD'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_query_active_submissions(self):
        """
        Test query for active submissions
        """
        url = '/api/submissions/items/?active=1'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_query_not_active_submissions(self):
        """
        Test query for not active submissions
        """
        url = '/api/submissions/items/?active=0'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_wrong_active_parameter(self):
        """
        Valid 'active' values are 0 and 1. Everything els should cause failure.
        """
        url = '/api/submissions/items/?active=3'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def test_query_status_and_active(self):
        """
        Usage of 'active' and 'ststus' together should cause failure
        """
        url = '/api/submissions/items/?active=1&status=submitted'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def test_multiple_parameters(self):
        """
        Test query with multiple parameters
        """
        url = '/api/submissions/items/?active=1&product=prod&name=%s' \
                                                      % self.fixture_obj.name
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """

        url = "/api/submissions/items/%d/" % (self.fixture_obj.pk,)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data[0])


    def test_get_not_existing_id(self):
        """
        GET requests to APIView should raise 404
        If it does not currently exist.
        """

        url = "/api/submissions/items/999/"
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_create(self):
        """"
        Test creation of new submission
        """
        url = "/api/submissions/items/"
        name = 'submit/product/20140407.000700'
        commit = '80392ccb45f80b554f99786b01ed7183899c2d1c'
        status = 'REJECTED'
        product = 'prod'
        response = self.client.post(url,
                       {'name': name, 'commit': commit,
                        'status': status, 'product': product},
                       HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        Submission.objects.get(name__exact=name, product__name__exact=product,
                               status__exact=status, commit__exact=commit)

    def test_create_duplicated(self):
        """
        Creation of duplicated submission should fail
        """
        url = "/api/submissions/items/"
        response = self.client.post(url, {'name': self.fixture_obj.name},
                                    HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
