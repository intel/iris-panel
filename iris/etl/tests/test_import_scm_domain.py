# -*- encoding: utf-8 -*-
'''
This module is used to test import scm data module: iris/etl/scm.py
'''

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain
from iris.core.models import DomainRole
from iris.etl.scm import from_string, ROLES

#pylint: skip-file


class DomainTest(unittest.TestCase):

    def tearDown(self):
        Domain.objects.all().delete()

    def test_add_one_domain(self):
        from_string("D: System", "")
        assert Domain.objects.get(name='System')

    def test_domain_name_include_colon(self):
        from_string("D: System:Test", "")
        assert Domain.objects.get(name='System:Test')

    def test_add_domain_dont_delete_others(self):
        from_string("D: Another", "")

        from_string('''
        D: Another
        D: System
        ''', '')
        assert Domain.objects.get(name="Another")

    def test_add_two_domains(self):
        from_string('''
            D: Another
            D: System
            ''', '')
        self.assertEqual(
            [('Another',), ('System',), ('Uncategorized',)],
            list(Domain.objects.all().order_by('name').values_list('name'))
            )

    def test_delete_two_domains(self):
        from_string('''
            D: Another
            D: System
            D: App Framework
            ''', '')
        from_string('D: App Framework', '')

        self.assertEqual(
            [('App Framework',)],
            list(Domain.objects.exclude(name='Uncategorized').values_list('name'))
            )

    def test_delete_all_domains(self):
        from_string('''
            D: Another
            D: System
            D: App Framework
            ''', '')
        from_string('', '')

        self.assertEqual(
            [('Uncategorized',)],
            list(Domain.objects.all().values_list('name'))
            )



class TestDomainRole(unittest.TestCase):
    def tearDown(self):
        DomainRole.objects.all().delete()
        Domain.objects.all().delete()
        User.objects.all().delete()

    def test_adding_domain_maintainer(self):
        from_string('''
        D: System
        M: Mike <mike@i.com>
        ''', '')

        self.assertEquals(
            [('mike@i.com',)],
            list(DomainRole.objects.get(
                    domain__name='System',
                    role='MAINTAINER').user_set.all(
                    ).values_list('email'))
            )

    def test_adding_two_domain_reviewers(self):
        from_string('''
        D: System
        R: Mike <mike@i.com>
        R: Lucy David <lucy.david@inher.com>
        ''', '')

        self.assertEqual(
            [(u'Lucy',), (u'Mike',)],
            list(DomainRole.objects.get(
                    domain__name='System',
                    role='REVIEWER').user_set.all(
                    ).order_by('first_name').values_list('first_name'))
            )

    def test_delete_integrators(self):
        from_string('''
        D: System
        I: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')
        from_string('''
        D: System
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')

        self.assertEqual(
            [('lily.edurd@inher.com',), ('lucy.david@inher.com',)],
            list(DomainRole.objects.get(
                    domain__name='System', role="INTEGRATOR").user_set.all(
                    ).order_by('email').values_list('email'))
            )

    def test_delete_all_roles(self):
        from_string('''
        D: System
        R: Mike <mike@i.com>
        A: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        M: <tom.edurd@inher.com>
        ''', '')
        from_string('''
        D: System
        ''', '')
        for role in ROLES:
            self.assertEqual(
            [],
            [r.role for r in DomainRole.objects.filter(
                domain__name='System', role=role)])

    def test_update_architectures(self):
        from_string('''
        D: System
        A: Mike <mike@i.com>
        ''', '')
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

        from_string('''
        D: System
        A: Mike Chung <mike@i.com>
        ''', '')

        self.assertEqual(
            [u'Chung'],
            [i.last_name for i in DomainRole.objects.get(
                    domain__name='System', role="ARCHITECT").user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_add_same_user_in_different_domain(self):
        from_string('''
        D: System
        A: Mike <mike@i.com>

        D: Appframework
        M: Mike <mike@i.com>
        ''', '')

        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in DomainRole.objects.get(
                    domain__name='System', role="ARCHITECT").user_set.all()])

        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in DomainRole.objects.get(
                    domain__name='Appframework', role="MAINTAINER").user_set.all()])

        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_roles_transform(self):
        from_string('''
        D: System
        A: Mike <mike@i.com>
        M: Lily David <lily.david@hello.com>
        R: Tom Frédéric <tom.adwel@hello.com>
        I: <lucy.chung@wel.com>
        ''', '')

        from_string('''
        D: System
        M: Mike <mike@i.com>
        R: Lily David <lily.david@hello.com>
        A: <lucy.chung@wel.com>
        I: Tom Frédéric <tom.adwel@hello.com>
        ''', '')
        self.assertEqual(
            ['lucy.chung@wel.com'],
            [i.email for i in DomainRole.objects.get(
                    domain__name='System', role="ARCHITECT").user_set.all()])

        self.assertEqual(
            ['lily.david@hello.com'],
            [i.email for i in DomainRole.objects.get(
                    domain__name='System', role="REVIEWER").user_set.all()])

        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in DomainRole.objects.get(
                    domain__name='System', role="MAINTAINER").user_set.all()])

        self.assertEqual(
            [u'Frédéric'],
            [i.last_name for i in DomainRole.objects.get(
                    domain__name='System', role="INTEGRATOR").user_set.all()])
        self.assertEqual(
            ['lily.david@hello.com',
             'lucy.chung@wel.com',
             'mike@i.com',
             'tom.adwel@hello.com'],
            [u.email for u in User.objects.all().order_by('email')])
