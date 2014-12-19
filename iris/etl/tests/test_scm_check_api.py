# -*- encoding: utf-8 -*-
# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
'''This mudule is used to test IRIS rest API: scm.check and scm_check in
iris/packagedb/views/scm.py
'''
import StringIO

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

#pylint: skip-file


class EventHandlerTest(TestCase):

    fixtures = ['users']

    def login(self, user='robot', pwd='robot'):
        assert self.client.login(username=user, password=pwd)

    def test_post_required(self):
        url = reverse('scm.check')
        self.login()
        r = self.client.get(url)
        self.assertEquals(405, r.status_code)

    def test_login_required(self):
        url = reverse('scm.check')
        r = self.client.post(url)
        self.assertEquals(403, r.status_code)

    def test_permission_required(self):
        url = reverse('scm.check')
        self.login('alice', 'alice')
        r = self.client.post(url)
        self.assertEquals(403, r.status_code)

    def test_missing_parameter(self):
        url = reverse('scm.check')
        self.login()
        r = self.client.post(url)
        self.assertEquals(406, r.status_code)

    def test_with_empty_file(self):
        self.login()
        domains = ''
        gittrees = ''
        domains_si = StringIO.StringIO(domains)
        domains_si.name = 'domains'
        gittrees_si = StringIO.StringIO(gittrees)
        gittrees_si.name = 'gittrees'

        r = self.client.post(reverse('scm.check'), {
                'domains': domains_si, 'gittrees': gittrees_si})
        self.assertEquals(406, r.status_code)

    def test_with_error_syntax_file(self):
        self.login()
        domains = '''
        D: System
        '''
        gittrees = '''
        adaptation/face-engine
        D: System
        '''
        domains_si = StringIO.StringIO(domains)
        domains_si.name = 'domains'
        gittrees_si = StringIO.StringIO(gittrees)
        gittrees_si.name = 'gittrees'

        r = self.client.post(reverse('scm.check'), {
                'domains': domains_si, 'gittrees': gittrees_si})
        self.assertEquals(406, r.status_code)

    def test_with_error_semantic_file(self):
        self.login()
        domains = '''
        D: System
        '''
        gittrees = '''
        T: adaptation/face-engine
        '''
        domains_si = StringIO.StringIO(domains)
        domains_si.name = 'domains'
        gittrees_si = StringIO.StringIO(gittrees)
        gittrees_si.name = 'gittrees'

        r = self.client.post(reverse('scm.check'), {
                'domains': domains_si, 'gittrees': gittrees_si})
        self.assertEquals(406, r.status_code)

    def test_with_no_error_file(self):
        self.login()
        domains = '''
        D: System
        '''
        gittrees = '''
        T: adaptation/face-engine
        D: System
        '''
        domains_si = StringIO.StringIO(domains)
        domains_si.name = 'domains'
        gittrees_si = StringIO.StringIO(gittrees)
        gittrees_si.name = 'gittrees'

        r = self.client.post(reverse('scm.check'), {
                'domains': domains_si, 'gittrees': gittrees_si})
        self.assertEquals(200, r.status_code)
