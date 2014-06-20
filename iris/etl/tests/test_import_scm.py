# -*- encoding: utf-8 -*-
'''
This module is used to test import scm data module: iris/etl/scm.py
'''

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain, GitTree
from iris.core.models import DomainRole, SubDomainRole, GitTreeRole, UserParty
from iris.etl import scm

#pylint: skip-file

class DomainTest(unittest.TestCase):

    def tearDown(self):
        Domain.objects.all().delete()

    def test_add_one_domain(self):
        scm.incremental_import_core("D: System", "")
        assert Domain.objects.get(name='System')

    def test_add_domain_dont_delete_others(self):
        scm.incremental_import_core("D: Another", "")

        scm.incremental_import_core('''
        D: Another
        D: System
        ''', '')
        assert Domain.objects.get(name="Another")

    def test_add_domains_count(self):
        scm.incremental_import_core('''
            D: Another
            D: System
            ''', '')
        self.assertEqual(['Another', 'System'], [domain.name for domain in
            Domain.objects.all().exclude(name='Uncategorized').order_by('name')
            ])

    def test_delete_domain(self):
        scm.incremental_import_core('''
            D: Another
            D: System
            D: App Framework
            ''', '')
        scm.incremental_import_core('''D: App Framework''', '')

        self.assertEqual(['App Framework'], [domain.name for domain in
            Domain.objects.all().exclude(name='Uncategorized').order_by('name')
            ])

class SubDomainTest(unittest.TestCase):

    def tearDown(self):
        SubDomainRole.objects.all().delete()
        Domain.objects.all().delete()

    def test_add_one_subdomain(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System
        ''', '')
        d = Domain.objects.get(name='System')
        assert 'Alarm' == SubDomain.objects.filter(domain=d).\
                          exclude(name='Uncategorized')[0].name

    def test_add_subdomain_dont_delete_others(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System
        ''', '')

        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')

        d = Domain.objects.get(name='System')
        assert 'Alarm' in [ i.name for i in SubDomain.objects.filter(domain=d)]

    def test_add_subdomains_count(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')
        d = Domain.objects.get(name='System')
        assert ['Alarm', 'Call' ]  == [ i.name for i in
                                SubDomain.objects.filter(domain=d).\
                                exclude(name='Uncategorized').order_by('name')]

    def test_delete_subdomain(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''', '')
        scm.incremental_import_core('''
        D: System

        D: System / Call
        N: System
        ''', '')

        d = Domain.objects.get(name='System')
        assert 'Call' == SubDomain.objects.filter(domain=d).\
                          exclude(name='Uncategorized')[0].name

class TestDomainRole(unittest.TestCase):
    def tearDown(self):
        DomainRole.objects.all().delete()
        Domain.objects.all().delete()
        User.objects.all().delete()

    def test_adding_domain_maintainer(self):
        scm.incremental_import_core('''
        D: System
        M: Mike <mike@i.com>
        ''', '')

        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="MAINTAINER")
        assert ['mike@i.com'] == [i.email for i in dr.user_set.all()]

    def test_adding_two_domain_reviewers(self):
        scm.incremental_import_core('''
        D: System
        R: Mike <mike@i.com>
        R: Lucy David <lucy.david@inher.com>
        ''', '')

        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="REVIEWER")
        self.assertEqual(['Lucy', 'Mike'],
                         [i.first_name.encode('utf8')
                          for i in dr.user_set.all().order_by('first_name')])

    def test_delete_integrators(self):
        scm.incremental_import_core('''
        D: System
        I: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')
        scm.incremental_import_core('''
        D: System
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''', '')

        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="INTEGRATOR")

        self.assertEqual(['lily.edurd@inher.com', 'lucy.david@inher.com'],
        [i.email for i in dr.user_set.all().order_by('email')])

    def test_update_architectures(self):
        scm.incremental_import_core('''
        D: System
        A: Mike <mike@i.com>
        ''', '')
        self.assertEqual(['mike@i.com'], [u.email for u in
        User.objects.all()])

        scm.incremental_import_core('''
        D: System
        A: Mike Chung <mike@i.com>
        ''', '')

        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="ARCHITECT")
        self.assertEqual(['Chung'], [i.last_name.encode('utf8')
                                     for i in dr.user_set.all()])
        self.assertEqual(['mike@i.com'], [u.email for u in User.objects.all()])

    def test_add_same_user_in_different_domain(self):
        scm.incremental_import_core('''
        D: System
        A: Mike <mike@i.com>

        D: Appframework
        M: Mike <mike@i.com>
        ''', '')

        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="ARCHITECT")
        self.assertEqual(['mike@i.com'], [i.email for i in dr.user_set.all()])

        d = Domain.objects.get(name='Appframework')
        dr = DomainRole.objects.get(domain=d, role="MAINTAINER")
        self.assertEqual(['mike@i.com'], [i.email for i in dr.user_set.all()])

        self.assertEqual(['mike@i.com'], [u.email for u in User.objects.all()])

    def test_roles_transform(self):
        scm.incremental_import_core('''
        D: System
        A: Mike <mike@i.com>
        M: Lily David <lily.david@hello.com>
        I: <lucy.chung@wel.com>
        ''', '')

        scm.incremental_import_core('''
        D: System
        M: Mike <mike@i.com>
        R: Lily David <lily.david@hello.com>
        A: <lucy.chung@wel.com>
        ''', '')
        d = Domain.objects.get(name='System')
        dr = DomainRole.objects.get(domain=d, role="ARCHITECT")
        self.assertEqual(['lucy.chung@wel.com'],
                         [i.email for i in dr.user_set.all()])
        dr = DomainRole.objects.get(domain=d, role="REVIEWER")
        self.assertEqual(['lily.david@hello.com'],
                         [i.email for i in dr.user_set.all()])
        dr = DomainRole.objects.get(domain=d, role="MAINTAINER")
        self.assertEqual(['mike@i.com'],
                         [i.email for i in dr.user_set.all()])
        self.assertEqual(['lily.david@hello.com',
                          'lucy.chung@wel.com',
                          'mike@i.com'],
        [u.email for u in User.objects.all().order_by('email')])
