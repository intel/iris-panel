# -*- encoding: utf-8 -*-
'''
This module is used to test import scm data module: iris/etl/scm.py
'''

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain
from iris.core.models import SubDomainRole
from iris.etl import scm

#pylint: skip-file

class TestSubDomainRole(unittest.TestCase):
    def tearDown(self):
        SubDomainRole.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()
        User.objects.all().delete()

    def test_add_subdomain_maintainer(self):
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        M: Mike <mike@i.com>
        ''', '')
        self.assertEqual(
               ['mike@i.com'],
               [i.email for i in SubDomainRole.objects.get(
               subdomain__name='Clock', role="MAINTAINER").user_set.all()])

    def test_adding_two_subdomain_reviewers(self):
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        R: Mike <mike@i.com>
        R: Lucy David <lucy.david@inher.com>
        ''', '')
        self.assertEqual(
             ['Lucy', 'Mike'],
             [i.first_name.encode('utf8') for i in SubDomainRole.objects.get(
              subdomain__name='Clock',
              role='REVIEWER').user_set.all().order_by('first_name')])

    def test_delete_integrators(self):
        ''' delete integrator: Mike <mike@i.com> '''

        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        I: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')
        self.assertEqual(
            ['lily.edurd@inher.com', 'lucy.david@inher.com'],
            [i.email for i in SubDomainRole.objects.get(
                subdomain__name='Clock',
                role='INTEGRATOR').user_set.all().order_by('email')])

    def test_update_architectures(self):
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        A: Mike <mike@i.com>
        ''', '')
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        A: Mike Frédéric <mike@i.com>
        ''', '')

        self.assertEqual(
            ['Frédéric'],
            [i.last_name.encode('utf8') for i in SubDomainRole.objects.get(
                subdomain__name='Clock', role='ARCHITECT').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_add_same_user_in_different_subdomain(self):
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        A: Mike <mike@i.com>

        D: Appframework

        D: Appframework / Gallery
        N: Appframework
        M: Mike <mike@i.com>
        ''', '')

        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in SubDomainRole.objects.get(
                subdomain__name='Clock', role='ARCHITECT').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in SubDomainRole.objects.get(
            subdomain__name='Gallery', role='MAINTAINER').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_roles_transform(self):
        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        A: Mike <mike@i.com>
        M: Lily David <lily.david@hello.com>
        I: <lucy.chung@wel.com>
        R: Tom Frédéric <tom.adwel@hello.com>
        ''', '')

        scm.incremental_import_core('''
        D: System

        D: System / Clock
        N: System
        M: Mike <mike@i.com>
        R: Lily David <lily.david@hello.com>
        A: <lucy.chung@wel.com>
        I: Tom Frédéric <tom.adwel@hello.com>
        ''', '')
        self.assertEqual(
                ['lucy.chung@wel.com'],
                [i.email for i in SubDomainRole.objects.get(
                    subdomain__name='Clock', role="ARCHITECT").user_set.all()])
        self.assertEqual(
                ['lily.david@hello.com'],
                [i.email for i in SubDomainRole.objects.get(
                    subdomain__name='Clock', role="REVIEWER").user_set.all()])
        self.assertEqual(
                ['mike@i.com'],
                [i.email for i in SubDomainRole.objects.get(
                   subdomain__name='Clock', role="MAINTAINER").user_set.all()])
        self.assertEqual(
                ['Frédéric'],
                [i.last_name.encode('utf8') for i in SubDomainRole.objects.get(
                   subdomain__name='Clock', role="INTEGRATOR").user_set.all()])
        self.assertEqual(['lily.david@hello.com',
                          'lucy.chung@wel.com',
                          'mike@i.com',
                          'tom.adwel@hello.com'],
                        [u.email for u in User.objects.all().order_by('email')])
