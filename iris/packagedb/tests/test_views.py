# -*- coding: utf-8 -*-

# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.

"""
This is the test module for the vanilla Django views for IRIS Package Database.

The tests included are mostly smoke tests for verifying that all views
indeed work correctly with legal input and produce a HTTP response code 200.
"""

# pylint: disable=E1101,E1103,R0904,C0103

from django.test import Client, TestCase
from django.contrib.auth.models import User

from iris.core.models import (Domain, SubDomain, License,
        GitTree, Package, Product, Image)
from iris.packagedb.plugin import APPINFO


def create_test_user():
    """
    Creates a test user with 'tester' username and password.

    Example usage::

        class Case(TestCase):
            def setUp(self):
                self.user = create_test_user()
    """

    admin = User.objects.create_user('admin', 'admin@test.com', 'admin')
    admin.is_superuser = True
    admin.save()

    return User.objects.create_user('tester', 'tester@test.com', 'tester')


def login(client, username='tester', password='tester'):
    """
    Uses the given client to login the given username and password.

    Example usage::

        class Case(TestCase):
            def setUp(self):
                self.client = Client()
                login(self.client)
    """

    return client.login(username=username, password=password)


def synthesize_url(postfix, base=None):
    """
    Creates url for the given URL postfix.

    If no param base is supplied, uses default base for plugin's app url.

    Base should include the last trailing slash: base='/baseurl/'

    Example usage::

        url = synthesize_url(postfix='domains/')
        url = synthesize_url(postfix='domains/', base='/custom/base/url')
    """

    # Default URL is of format '^url/', we'll want to clean out the caret
    base = base or APPINFO['urlpatterns']['baseurl'].replace('^', '/')
    return base + postfix


class DomainTest(TestCase):
    """
    Tests for creating, reading and deleting Domain objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client and Domain fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.domain = Domain.objects.create(name='Multimedia')

    def test_create_domain(self):
        """
        Creates a Domain object with POST.
        """

        data = {
            'name': 'Multimedia',
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('domains/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_domains(self):
        """
        Reads all Domain objects with GET.
        """

        url = synthesize_url('domains/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_domain(self):
        """
        Reads a single Domain object with GET.
        """

        url = synthesize_url('domains/%d/' % self.domain.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_domain(self):
        """
        Deletes a single Domain object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('domains/%d/delete/' % self.domain.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class SubDomainTest(TestCase):
    """
    Tests for creating, reading and deleting SubDomain objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client and SubDomain fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.domain = Domain.objects.create(name='Multimedia')
        self.subdomain = SubDomain.objects.create(name='SubMultimedia',
            domain=self.domain)

    def test_create_subdomain(self):
        """
        Creates a SubDomain object with POST.
        """

        data = {
            'name': 'SubMultimedia',
            'subdomain': '%d' % self.domain.pk,
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('subdomains/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_subdomains(self):
        """
        Reads all SubDomain objects with GET.
        """

        url = synthesize_url('subdomains/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_subdomain(self):
        """
        Reads a single SubDomain object with GET.
        """

        url = synthesize_url('subdomains/%d/' % self.subdomain.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_subdomain(self):
        """
        Deletes a single SubDomain object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('subdomains/%d/delete/' % self.subdomain.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class LicenseTest(TestCase):
    """
    Tests for creating, reading and deleting license objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client and License fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.license = License.objects.create(
                shortname='LGPL 2.1',
                text='Lorem ipsum dolor, sit amet qualitet.')

    def test_create_license(self):
        """
        Creates a License object with POST.
        """

        data = {
            'shortname': 'LGPL 2.0',
            'text': 'Lorem ipsum dolor, sit amet qualitet.',
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('licenses/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_licenses(self):
        """
        Reads all License objects with GET.
        """

        url = synthesize_url('licenses/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_license(self):
        """
        Reads a single License object with GET.
        """

        url = synthesize_url('licenses/%d/' % self.license.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_license(self):
        """
        Deletes a single License object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('licenses/%d/delete/' % self.license.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class GitTreeTest(TestCase):
    """
    Tests for creating, reading and deleting GitTree objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client, Domain, SubDomain and GitTree fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.domain = Domain.objects.create(name='Multimedia')
        self.subdomain = SubDomain.objects.create(name='SubMultimedia',
                domain=self.domain)
        self.gittree = GitTree.objects.create(
                gitpath='/pulseaudio/libpulseaudio',
                subdomain=self.subdomain)

    def test_create_gittree(self):
        """
        Creates a GitTree object with POST.
        """

        data = {
            'gitpath': '/pulseaudio/libpulseaudio',
            'subdomain': '%d' % self.subdomain.id
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('gittrees/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_gittrees(self):
        """
        Reads all GitTree objects with GET.
        """

        url = synthesize_url('gittrees/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_gittree(self):
        """
        Reads a single GitTree object with GET.
        """

        url = synthesize_url('gittrees/%d/' % self.gittree.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_gittree(self):
        """
        Deletes a single GitTree object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('gittrees/%d/delete/' % self.gittree.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class PackageTest(TestCase):
    """
    Tests for creating, reading and deleting Package objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client, Domain, GitTree and Package fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.domain = Domain.objects.create(name='Multimedia')
        self.subdomain = SubDomain.objects.create(name='SubMultimedia',
                domain=self.domain)
        self.gittree = GitTree.objects.create(
                gitpath='/pulseaudio/libpulseaudio',
                subdomain=self.subdomain)
        self.package = Package.objects.create(
                name='Pulseaudio',
                gittree=self.gittree)

    def test_create_package(self):
        """
        Creates a Package object with POST.
        """

        data = {
            'name': '/alsa/libalsa',
            'gittree': '%d' % self.gittree.id
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('packages/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_packages(self):
        """
        Reads all Package objects with GET.
        """

        url = synthesize_url('packages/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_package(self):
        """
        Reads a single Package object with GET.
        """

        url = synthesize_url('packages/%d/' % self.package.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_package(self):
        """
        Deletes a single Package object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('packages/%d/delete/' % self.package.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class ProductTest(TestCase):
    """
    Tests for creating, reading and deleting Product objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client and Product fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.product = Product.objects.create(name='Tizen Common',
                description='Foo, Bar, Biz, Bah')

    def test_create_product(self):
        """
        Creates a Product object with POST.
        """

        data = {
            'name': 'Tizen IVI',
            'description': 'Tizen IVI',
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('products/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_products(self):
        """
        Reads all Product objects with GET.
        """

        url = synthesize_url('products/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_product(self):
        """
        Reads a single Product object with GET.
        """

        url = synthesize_url('products/%d/' % self.product.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_product(self):
        """
        Deletes a single Product object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('products/%d/delete/' % self.product.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)


class ImageTest(TestCase):
    """
    Tests for creating, reading and deleting Image objects.
    """

    def setUp(self):
        """
        Sets tests up with User, Client and Product and Image fixtures.
        """

        self.user = create_test_user()
        self.client = Client()
        login(self.client)

        self.product = Product.objects.create(name='Tizen Common',
                description='Foo, Bar, Biz, Bah')
        self.image = Image.objects.create(name='Tizen IVI',
                target='Tizen IVI', arch='x86', product=self.product)

    def test_create_image(self):
        """
        Creates a Image object with POST.
        """

        data = {
            'name': 'Tizen PC',
            'target': 'Tizen PC',
            'arch': 'x86',
            'product': '%d' % self.product.id
        }

        login(self.client, username='admin', password='admin')
        url = synthesize_url('images/create/')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_read_images(self):
        """
        Reads all Image objects with GET.
        """

        url = synthesize_url('images/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_read_image(self):
        """
        Reads a single Image object with GET.
        """

        url = synthesize_url('images/%d/' % self.image.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_delete_image(self):
        """
        Deletes a single Image object with DELETE.
        """

        login(self.client, username='admin', password='admin')
        url = synthesize_url('images/%d/delete/' % self.image.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
