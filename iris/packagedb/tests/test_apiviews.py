# -*- coding: utf-8 -*-

#This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the REST framework test class for the iris-packagedb project REST API.
"""

# pylint: disable=E1101,E1103,R0904,C0103

import base64
from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
    Product, Image)


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

        url = '/api/packagedb/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.data,
            {u'detail': u'Authentication credentials were not provided.'})


    def test_auth_success(self):
        """
        Login success should return True.
        """
        url = '/api/packagedb/products/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertTrue(response)


class ProductsTests(TestCase):
    """
    The REST framework test case class of Product APIView
    """

    def setUp(self):
        """
        Create 1 Product instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        self.fixture_obj = Product.objects.create(name='product',
            short='short', state='open', targets='product')
        self.data = [{'name': obj.name, 'short': obj.short,
                      'state': obj.state, 'targets': obj.targets,
                      'gittrees': [item for item in obj.gittrees.all()]
                     } for obj in Product.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/products/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)


    def test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """

        url = "/api/packagedb/products/%d/" % (self.fixture_obj.pk,)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data[0])


    def test_get_not_deleted_detail(self):
        """
        GET requests to APIView should raise 404
        If it does not currently exist.
        """

        url = "/api/packagedb/products/999/"
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 404)


class DomainsTests(TestCase):
    """
    The REST framework test case class of Domain APIView
    """

    def setUp(self):
        """
        Create 1 Domain instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        Domain.objects.create(name='domain')
        self.data = [{'name': obj.name}for obj in Domain.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/domains/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)


class SubDomainsTests(TestCase):
    """
    The REST framework test case class of SubDomain APIView
    """

    def setUp(self):
        """
        Create 1 SubDomain instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        domain = Domain.objects.create(name='domain')
        SubDomain.objects.create(name='subdomain', domain=domain)
        self.data = [{'name': obj.name, 'domain': obj.domain.id}
                     for obj in SubDomain.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/subdomains/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)


class LicensesTests(TestCase):
    """
    The REST framework test case class of License APIView
    """

    def setUp(self):
        """
        Create 1 License instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        License.objects.create(fullname='license', shortname='lic')
        self.data = [{'fullname': obj.fullname, 'shortname': obj.shortname,
                      'url': obj.url, 'notes': obj.notes, 'active': obj.active,
                      'text': obj.text, 'text_updatable': obj.text_updatable,
                      'md5': obj.md5, 'detector_type': obj.detector_type
                     } for obj in License.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/licenses/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)



class GitTreesTests(TestCase):
    """
    The REST framework test case class of GitTree APIView
    """

    def setUp(self):
        """
        Create 1 GitTree instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        domain = Domain.objects.create(name='domain')
        subdomain = SubDomain.objects.create(name='subdomain', domain=domain)
        GitTree.objects.create(gitpath='gitpath', subdomain=subdomain)
        self.data = [{'gitpath': obj.gitpath, 'subdomain': obj.subdomain.pk,
                      'licenses': [item for item in obj.licenses.all()]
                     } for obj in GitTree.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/gittrees/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)


class PackagesTests(TestCase):
    """
    The REST framework test case class of Package APIView
    """

    def setUp(self):
        """
        Create 1 Package instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        domain = Domain.objects.create(name='domain')
        subdomain = SubDomain.objects.create(name='subdomain', domain=domain)
        gt = GitTree.objects.create(gitpath='gitpath', subdomain=subdomain)
        Package.objects.create(name='package', gittree=gt)
        self.data = [{'name': obj.name, 'gittree': obj.gittree.pk
                     } for obj in Package.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/packages/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)


class ImagesTests(TestCase):
    """
    The REST framework test case class of Image APIView
    """

    def setUp(self):
        """
        Create 1 Image instance.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        product = Product.objects.create(name='product')
        Image.objects.create(name='image', target='target',
            arch='arch', product=product)
        self.data = [{'name': obj.name, 'target': obj.target,
                      'arch': obj.arch, 'product': obj.product.pk
                     } for obj in Image.objects.all()]


    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """

        url = '/api/packagedb/images/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.data)
