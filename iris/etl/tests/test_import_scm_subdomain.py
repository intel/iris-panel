# -*- encoding: utf-8 -*-
'''
This module is used to test import scm data module: iris/etl/scm.py
'''

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain, SubDomainRole
from iris.etl.scm import from_string, ROLES

#pylint: skip-file

class SubDomainTest(unittest.TestCase):

    def tearDown(self):
        SubDomainRole.objects.all().delete()
        Domain.objects.all().delete()

    def test_add_one_subdomain(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System
        ''', '')
        self.assertEquals(
            [('Alarm', )],
            list(SubDomain.objects.filter(
                    domain__name='System').exclude(
                    name='Uncategorized').values_list('name'))
            )
    def test_subdomain_includes_slash_colon(self):
        from_string('''
        D: System

        D: System / Alarm:Clock/Hash
        N: System
        ''', '')
        self.assertEquals(
            [('Alarm:Clock/Hash', )],
            list(SubDomain.objects.filter(
                    domain__name='System').exclude(
                    name='Uncategorized').values_list('name'))
            )


    def test_add_subdomain_dont_delete_others(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System
        ''', '')

        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')

        assert SubDomain.objects.get(domain__name='System', name='Alarm')

    def test_add_two_subdomains(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')
        self.assertEqual(
            [('Alarm',), ('Call',)],
            list(SubDomain.objects.filter(
                    domain__name='System').exclude(
                    name='Uncategorized').order_by(
                    'name').values_list('name'))
            )

    def test_delete_one_subdomain(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')
        from_string('''
        D: System

        D: System / Call
        N: System
        ''', '')

        self.assertEqual(
            'Call',
            SubDomain.objects.filter(
                domain__name='System').exclude(
                name='Uncategorized')[0].name
            )

    def test_delete_all_subdomains(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')
        from_string('D: System', '')

        self.assertEqual(
            ['Uncategorized'],
            [s.name for s in SubDomain.objects.filter(domain__name='System')])

    def test_update_subdomain(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System
        ''', '')
        from_string('''
        D: System
        D: App

        D: App / Alarm
        N: App
        ''', '')

        self.assertEqual(
            'Alarm',
            SubDomain.objects.filter(
                domain__name='App').exclude(
                name='Uncategorized')[0].name
            )
        self.assertFalse(
            SubDomain.objects.filter(
                domain__name='System').exclude(
                name='Uncategorized')
            )

class TestSubDomainRole(unittest.TestCase):
    def tearDown(self):
        SubDomainRole.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()
        User.objects.all().delete()

    def test_add_subdomain_maintainer(self):
        from_string('''
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
        from_string('''
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

        from_string('''
        D: System

        D: System / Clock
        N: System
        I: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')
        from_string('''
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

    def test_delete_all_roles(self):
        from_string('''
        D: System

        D: System / Clock
        N: System
        R: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        M: <lily.edurd@inher.com>
        A: <tom.edurd@inher.com>
        ''', '')
        from_string('''
        D: System

        D: System / Clock
        N: System
        ''', '')
        for role in ROLES:
            self.assertEqual(
              [],
              [r.role for r in SubDomainRole.objects.filter(
                subdomain__name='Clock', role=role)])

    def test_update_architectures(self):
        from_string('''
        D: System

        D: System / Clock
        N: System
        A: Mike <mike@i.com>
        ''', '')
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

        from_string('''
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
        from_string('''
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
        from_string('''
        D: System

        D: System / Clock
        N: System
        A: Mike <mike@i.com>
        M: Lily David <lily.david@hello.com>
        I: <lucy.chung@wel.com>
        R: Tom Frédéric <tom.adwel@hello.com>
        ''', '')

        from_string('''
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
