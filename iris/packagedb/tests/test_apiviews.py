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

#pylint: disable=no-member,missing-docstring,invalid-name
#E:397,18: Instance of 'HttpResponse' has no 'data' member (no-member)
#C: 36, 0: Missing function docstring (missing-docstring)
#C: 96, 8: Invalid variable name "d" (invalid-name)

import base64
import urllib

from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (
    Domain, SubDomain, GitTree, Package, Product, License, DomainRole,
    SubDomainRole, GitTreeRole)


def sort_data(data):
    if isinstance(data, list):
        data.sort()
        for item in data:
            sort_data(item)

    if isinstance(data, dict):
        for value in data.itervalues():
            sort_data(value)


class ProductsTests(TestCase):
    """
    The REST framework test case class of Product APIView
    """

    def setUp(self):
        """
        Create 2 Product instance. One includes 2 gittrees, the other includes
        1 gittree.
        Create 2 test user.
        """
        user = User.objects.create_user(username='nemo', password='password')

        d = Domain.objects.create(name='doamin')
        sd = SubDomain.objects.create(name='subdoamin', domain=d)
        gt1 = GitTree.objects.create(gitpath='a/b', subdomain=sd)
        gt2 = GitTree.objects.create(gitpath='c/d', subdomain=sd)
        p1 = Product.objects.create(name='product', description='product1')
        p2 = Product.objects.create(name='a:b', description='product2')
        p1.gittrees.add(gt1, gt2)
        p2.gittrees.add(gt2)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/products/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = [{
            'name': 'a:b',
            'description': 'product2',
            'gittrees': ['c/d']
        }, {
            'name': 'product',
            'description': 'product1',
            'gittrees': ['a/b', 'c/d']
        }]

        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """
        url = "/api/packagedb/products/a:b/"
        url = urllib.quote(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'name': 'a:b',
            'description': 'product2',
            'gittrees': ['c/d'],
        }
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)

    def test_get_not_deleted_detail(self):
        """
        GET requests to APIView should raise 404
        If it does not currently exist.
        """
        url = "/api/packagedb/products/999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class DomainsTests(TestCase):
    """
    The REST framework test case class of Domain APIView
    """

    def setUp(self):
        """
        Create 2 SubDomain instance, one of them is 'Uncategorized',
        one domainrole, one subdomainrole.
        Create 2 test user.
        """
        user = User.objects.create_user(
            username='nemo', password='password', email='nemo@a.com')
        user2 = User.objects.create_user(
            username='lucy', password='lucy',
            first_name='jaeho81', last_name='lucy',
            email='jaeho81.lucy@a.com')

        d1 = Domain.objects.create(name='domain1')
        d2 = Domain.objects.create(name='domain2')
        sd1 = SubDomain.objects.create(name='subdomain', domain=d1)
        SubDomain.objects.create(name='Uncategorized', domain=d2)

        dr = DomainRole.objects.create(
            role='Architect', domain=d2,
            name="%s: %s" % ('Architect', d2.name))
        user.groups.add(dr)
        user2.groups.add(dr)
        sdr = SubDomainRole.objects.create(
            role='Maintainer', subdomain=sd1,
            name="%s: %s" % ('Maintainer', sd1.name))
        user.groups.add(sdr)
        user2.groups.add(sdr)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/domains/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = [{
            'name': 'domain1 / subdomain',
            'roles': {
                'Maintainer': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com',
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }]
            },
        }, {
            'name': 'domain2 / Uncategorized',
            'roles': {
                'Architect': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com'
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }],
            },
        }]
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return single objects.
        """
        url = '/api/packagedb/domains/domain2 / Uncategorized/'
        url = urllib.quote(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'name': 'domain2 / Uncategorized',
            'roles': {
                'Architect': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com'
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }],
            }
        }
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)


class GitTreesTests(TestCase):
    """
    The REST framework test case class of GitTree APIView
    """

    def setUp(self):
        """
        Create 2 GitTree instance. One realted with domain, two packages,
        another one realted with subdomain, one license.
        with subdomain,
        Create 2 test user.
        """
        user1 = User.objects.create_user(
            username='nemo', password='password', email='nemo@a.com')
        user2 = User.objects.create_user(
            username='lucy', password='password',
            first_name='jaeho81', last_name='lucy',
            email='jaeho81.lucy@a.com')

        domain = Domain.objects.create(name='domain')
        sd1 = SubDomain.objects.create(name='subdomain', domain=domain)
        sd2 = SubDomain.objects.create(name='Uncategorized', domain=domain)

        gt1 = GitTree.objects.create(gitpath='d/f', subdomain=sd1)
        gt2 = GitTree.objects.create(gitpath='a/b/c', subdomain=sd2)

        p1 = Package.objects.create(name='xap1')
        p2 = Package.objects.create(name='p2')
        gt1.packages.add(p1, p2)
        gt2.packages.add(p2)

        l1 = License.objects.create(shortname='license1',
                                    fullname='labc def',
                                    text='helo')
        l2 = License.objects.create(shortname='abc',
                                    fullname='weldome sdfs',
                                    text='helo world')
        gt2.licenses.add(l1, l2)

        gr1 = GitTreeRole.objects.create(
            role='Integrator', gittree=gt1,
            name='Integrator: %s' % gt1.gitpath)
        user1.groups.add(gr1)
        user2.groups.add(gr1)
        gr2 = GitTreeRole.objects.create(
            role='Maintainer', gittree=gt2,
            name='Integrator: %s' % gt2.gitpath)
        user1.groups.add(gr2)
        user2.groups.add(gr2)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/gittrees/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = [{
            'gitpath': 'a/b/c',
            'domain': 'domain / Uncategorized',
            'roles': {
                'Maintainer': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com'
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }],
            },
            'packages': ['p2'],
            'licenses': ['license1', 'abc'],
        }, {
            'gitpath': 'd/f',
            'domain': 'domain / subdomain',
            'roles': {
                'Integrator': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com'
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }]
            },
            'packages': ['xap1', 'p2'],
            'licenses': [],
        }]
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return single objects.
        """
        url = '/api/packagedb/gittrees/d/f/'
        url = urllib.quote(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {
            'gitpath': 'd/f',
            'domain': 'domain / subdomain',
            'roles': {
                'Integrator': [{
                    'first_name': '',
                    'last_name': '',
                    'email': 'nemo@a.com'
                }, {
                    'first_name': 'jaeho81',
                    'last_name': 'lucy',
                    'email': 'jaeho81.lucy@a.com'
                }],
            },
            'packages': ['xap1', 'p2'],
            'licenses': [],
        }
        sort_data(data)
        sort_data(response.data)
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

        domain = Domain.objects.create(name='domain')
        subdomain = SubDomain.objects.create(name='subdomain', domain=domain)
        gt1 = GitTree.objects.create(gitpath='agitpath1', subdomain=subdomain)
        gt2 = GitTree.objects.create(gitpath='gitpath2', subdomain=subdomain)

        pack1 = Package.objects.create(name='package1')
        pack2 = Package.objects.create(name='package2')
        gt1.packages.add(pack1, pack2)
        gt2.packages.add(pack2)

    def test_get_info(self):
        """
        GET requests to APIView should return list of objects.
        """
        url = '/api/packagedb/packages/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = [{
            'name': 'package1',
            'gittrees': ['agitpath1']
        }, {
            'name': 'package2',
            'gittrees': ['gitpath2', 'agitpath1']
        }]
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)

    def test_get_detail(self):
        """
        GET requests to APIView should return a single object.
        """
        url = '/api/packagedb/packages/package2/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = {'name': 'package2', 'gittrees': ['agitpath1', 'gitpath2']}
        sort_data(data)
        sort_data(response.data)
        self.assertEqual(response.data, data)
