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
import urllib

from django.test import TestCase
from django.contrib.auth.models import User

from rest_framework.status import (
    HTTP_200_OK, HTTP_404_NOT_FOUND,
    HTTP_406_NOT_ACCEPTABLE, HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST)

from iris.core.models import (
    Product, Submission, Domain, SubDomain, GitTree, BuildGroup,
    SubmissionBuild, PackageBuild, Package)
from iris.packagedb.tests.test_apiviews import sort_data

# pylint: disable=no-member,invalid-name,eval-used,too-many-locals
#E:266,25: Instance of 'WSGIRequest' has no 'data' member (no-member)
#C:236, 4: Invalid method name "_test_query_not_active_submissions" (invalid-name)
#W:143,19: Use of eval (eval-used)
#R: 73, 4: Too many local variables (18/15) (too-many-locals)


class AuthTests(TestCase):
    """
    The REST framework test case class of Authorization
    """

    def setUp(self):
        """
        Create 1 test user.
        """
        User.objects.create_user(username='nemo', password='password')
        self.base_url = '/api/submissions'

    def test_auth_fail(self):
        """
        Get requests to APIView should raise 403
        if dose not sign in.
        """
        url = '%s/Tizen:Common/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data, {
            u'detail': u'Authentication credentials were not provided.'})

    def test_auth_success(self):
        """
        Login success should return True.
        """
        url = '%s/Tizen:Common/' % self.base_url
        self.client.login(username='nemo', password='password')
        response = self.client.get(url)
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
        self.base_url = '/api/submissions'
        user = User.objects.create_user(username='nemo', password='password')
        self.client.login(username='nemo', password='password')

        product = Product.objects.create(name='Tizen:Common', description='Product')
        d = Domain.objects.create(name='domain')
        sd = SubDomain.objects.create(name='subdomain', domain=d)
        gt = GitTree.objects.create(gitpath='gitpath', subdomain=sd)

        submission_name_status = {
            'submit/product/20140321.223750': '20_IMGBUILDING',
            'submit/product/20140421.223750': '15_PKGFAILED',
            'submit/product/20140521.223750': '15_PKGFAILED',
            'submit/product/20140621.223750': '33_ACCEPTED',
            'submit/product/20140721.223750': '36_REJECTED'
        }
        for key, value in submission_name_status.iteritems():
            sb1 = Submission.objects.create(
                name=key,
                commit='2ae265f9820cb36e',
                owner=user,
                gittree=gt,
                status=value)
            bg1 = BuildGroup.objects.create(
                name='home:pre-release:Tizen:Common:%s' % key,
                status=value)
            SubmissionBuild.objects.create(
                submission=sb1,
                product=product,
                group=bg1)

        buildgroup_name_packages_status = {
            'submit/product/20140321.223750': [('pac1', 'pac3'), 'SUCCESS'],
            'submit/product/20140421.223750': [('pac2',), 'FAILURE'],
            'submit/product/20140521.223750': [('pac1',), 'FAILURE'],
        }
        for key, value in buildgroup_name_packages_status.iteritems():
            bg = BuildGroup.objects.get(name='home:pre-release:Tizen:Common:%s' % key)
            packages, status = value
            for pac in packages:
                p, _ = Package.objects.get_or_create(name=pac)
                PackageBuild.objects.create(package=p, group=bg, status=status)

    def test_get_query_by_product(self):
        """
        GET full list of submissions
        """
        url = '%s/Tizen:Common/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = [{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'packages': ['pac1', 'pac3']
        }, {
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'packages': ['pac2']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'packages': ['pac1']
        }]
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def _test_query_by_name(self):
        """
         GET submissions by name.
        """
        url = '/api/submissions/items/?name=submit/product/20140321.223750'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def _test_empty_query_by_name(self):
        """"
        GET empty results by querying by non-existing name
        """
        url = '/api/submissions/items/?name=this_submission_doesnt_exist'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_query_by_un_exist_product(self):
        """
        Test failed query by querying non-existing product
        """
        url = '%s/this_product_doesnt_exist/' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(eval(response.content), [])

    def test_query_by_status(self):
        """
        GET submissions by status
        """
        url = '%s/Tizen:Common/?status=%s' % \
              (self.base_url, urllib.quote('Package building failed'))
        data = [{
            'submission': 'submit/product/20140421.223750',
            'status': 'Package building failed',
            'packages': ['pac2']
        }, {
            'submission': 'submit/product/20140521.223750',
            'status': 'Package building failed',
            'packages': ['pac1']
        }]
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def test_by_un_exist_status(self):
        """
        Test failed query by querying non-existing status
        """
        url = '%s/Tizen:Common/?status=hello' % self.base_url
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(eval(response.content), [])

    def test_case_insensitive_status(self):
        """
        Test that status can be case insensitive
        """
        url = '%s/Tizen:Common/?status=%s' % \
            (self.base_url, urllib.quote('image building'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTP_200_OK)
        data = [{
            'submission': 'submit/product/20140321.223750',
            'status': 'Image building',
            'packages': ['pac1', 'pac3']
            }]
        res_data = eval(response.content)
        sort_data(data)
        sort_data(res_data)
        self.assertEqual(res_data, data)

    def _test_query_active_submissions(self):
        """
        Test query for active submissions
        """
        url = '/api/submissions/items/?active=1'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def _test_query_not_active_submissions(self):
        """
        Test query for not active submissions
        """
        url = '/api/submissions/items/?active=0'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, [])

    def _test_wrong_active_parameter(self):
        """
        Valid 'active' values are 0 and 1. Everything els should cause failure.
        """
        url = '/api/submissions/items/?active=3'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def _test_query_status_and_active(self):
        """
        Usage of 'active' and 'ststus' together should cause failure
        """
        url = '/api/submissions/items/?active=1&status=submitted'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_406_NOT_ACCEPTABLE)

    def _test_multiple_parameters(self):
        """
        Test query with multiple parameters
        """
        url = '/api/submissions/items/?active=1&product=prod&name=%s' \
                                                      % self.fixture_obj.name
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data)

    def _test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """

        url = "/api/submissions/items/%d/" % (self.fixture_obj.pk,)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(response.data, self.data[0])


    def _test_get_not_existing_id(self):
        """
        GET requests to APIView should raise 404
        If it does not currently exist.
        """

        url = "/api/submissions/items/999/"
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def _test_create(self):
        """"
        Test creation of new submission
        """
        url = "/api/submissions/items/"
        name = 'submit/product/20140407.000700'
        commit = '80392ccb45f80b554f99786b01ed7183899c2d1c'
        status = 'REJECTED'
        product = 'prod'
        response = self.client.post(
            url, {
                'name': name, 'commit': commit,
                'status': status, 'product': product
            },
            HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_201_CREATED)
        Submission.objects.get(name__exact=name, product__name__exact=product,
                               status__exact=status, commit__exact=commit)

    def _test_create_duplicated(self):
        """
        Creation of duplicated submission should fail
        """
        url = "/api/submissions/items/"
        response = self.client.post(url, {'name': self.fixture_obj.name},
                                    HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
