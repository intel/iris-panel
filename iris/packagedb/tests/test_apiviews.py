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
#pylint: skip-file

import base64
import urllib

from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (Domain, SubDomain, License, GitTree, Package,
    Product, Image, GitTreeRole)


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
        Create 2 Product instance. One includes 2 gittrees, the other includes
        1 gittree.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        d = Domain.objects.create(name='doamin')
        sd = SubDomain.objects.create(name='subdoamin', domain=d)
        gt1 = GitTree.objects.create(gitpath='a/b', subdomain=sd)
        gt2 = GitTree.objects.create(gitpath='c/d', subdomain=sd)
        self.fixture_obj1 = Product.objects.create(name='product',
            description='product2')
        self.fixture_obj2 = Product.objects.create(name='a:b',
            description='product2')
        self.fixture_obj1.gittrees.add(gt1, gt2)
        self.fixture_obj2.gittrees.add(gt2)

        self.data = [{'name': obj.name,'description': obj.description,
                      'gittrees': [item.gitpath for item in obj.gittrees.all()]
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
        url = "/api/packagedb/products/%s/" % (self.fixture_obj2.name,)
        url = urllib.quote(url)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
                    {'name': self.fixture_obj2.name,
                     'description': self.fixture_obj2.description,
                    'gittrees': [item.gitpath for item in self.fixture_obj2.gittrees.all()]
                    })

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


class GitTreesTests(TestCase):
    """
    The REST framework test case class of GitTree APIView
    """

    def setUp(self):
        """
        Create 2 GitTree instance. One realted with domain, two packages,
        another one realted with subdomain, one license.
        with subdomain,
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        domain = Domain.objects.create(name='domain')
        sd1  = SubDomain.objects.create(name='subdomain', domain=domain)
        sd2  = SubDomain.objects.create(name='Uncategorized', domain=domain)

        self.gt1 = GitTree.objects.create(gitpath='d/f', subdomain=sd1)
        self.gt2 = GitTree.objects.create(gitpath='a/b/c', subdomain=sd2)

        p1 = Package.objects.create(name='p1')
        p2 = Package.objects.create(name='p2')
        self.gt1.packages.add(p1, p2)

        l1 = License.objects.create(shortname='l1',
                                    fullname='labc def',
                                    text='helo')
        self.gt2.licenses.add(l1)

        GitTreeRole.objects.create(role='Integrator', gittree=self.gt1, name='Integrator: %s' % self.gt1.gitpath)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/gittrees/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        data = [{'gitpath': obj.gitpath,
                'domain': ' / '.join((obj.subdomain.domain.name, obj.subdomain.name)),
                'licenses': [item.shortname for item in obj.licenses.all()],
                'packages': [item.name for item in obj.packages.all()],
                'roles': obj.roles()
                } for obj in GitTree.objects.all()]

        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return single objects.
        """
        url = '/api/packagedb/gittrees/%s/' % self.gt1.gitpath
        url = urllib.quote(url)
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        data = {'gitpath': self.gt1.gitpath,
                'domain': ' / '.join((self.gt1.subdomain.domain.name, self.gt1.subdomain.name)),
                'roles': self.gt1.roles(),
                'packages': [item.name for item in self.gt1.packages.all()],
                'licenses': [item.shortname for item in self.gt1.licenses.all()],
                }

        self.assertEqual(response.data, data)


class PackagesTests(TestCase):
    """
    The REST framework test case class of Package APIView
    """

    def setUp(self):
        """
        Create 2 Package instance, one realted with two gittrees, the other
        related with 1 gittree.
        Create 1 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')
        self.credentials = basic_auth_header(user.username, 'password')

        domain = Domain.objects.create(name='domain')
        subdomain = SubDomain.objects.create(name='subdomain', domain=domain)
        self.gt1 = GitTree.objects.create(gitpath='gitpath1', subdomain=subdomain)
        self.gt2 = GitTree.objects.create(gitpath='gitpath2', subdomain=subdomain)

        self.pack1 = Package.objects.create(name='package1')
        self.pack2 = Package.objects.create(name='package2')
        self.gt1.packages.add(self.pack1, self.pack2)
        self.gt2.packages.add(self.pack2)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/packages/'
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        data = [
                {'name': self.pack1.name, 'gittrees': [self.gt1.gitpath]},
                {'name': self.pack2.name, 'gittrees': [self.gt1.gitpath, self.gt2.gitpath]},
               ]
        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """
        url = '/api/packagedb/packages/%s/' % self.pack2.name
        response = self.client.get(url, HTTP_AUTHORIZATION=self.credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data,
            {'name': self.pack2.name, 'gittrees': [self.gt1.gitpath, self.gt2.gitpath]})
