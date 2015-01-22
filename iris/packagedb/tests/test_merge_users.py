# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
import sys
import os
import time

from django.test import TestCase
from django.contrib.auth.models import User
from iris.core.models import Domain, DomainRole

from iris.etl.scm import merge_users

#pylint: skip-file


class MergeUsersTest(TestCase):

    def setUp(self):
        self.mail = 'test@test.com'
        self.user_a = User.objects.create_user(self.mail, self.mail, 'testa')
        domain = Domain.objects.create(name='domain')
        self.domainrole = DomainRole.objects.create(role='domainrole', domain=domain)
        self.domainrole.user_set.add(self.user_a)
        self.user_b = User.objects.create_user('testb', self.mail, 'testb')

    def tearDown(self):
        User.objects.all().delete()
        DomainRole.objects.all().delete()

    def test_merge_users(self):
        merge_users(self.mail)
        self.assertEqual(User.objects.filter(username=self.mail, email=self.mail).exists(), False)
        self.assertTrue(self.user_b in self.domainrole.user_set.all(), True)
        self.assertTrue(len(self.domainrole.user_set.all()) == 1, True)


if __name__ == '__main__':
     unittest.main()
