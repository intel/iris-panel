# -*- encoding: utf-8 -*-
'''
    This module is used to test Domain Model changes
'''

import os
import copy
import unittest
from iris.core.models import Domain
from iris.etl import scm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIXTURE_PATH = os.path.join(BASE_DIR, 'fixtures')

class DomainTest(unittest.TestCase):
    ''' test init, add, delete '''

    sources = ['App Framework', 'Multimedia', 'Uncategorized']

    def import_scm(self, domain, gittree):
        ''' import scm data '''
        domain = os.path.join(FIXTURE_PATH, domain)
        gittree = os.path.join(FIXTURE_PATH, gittree)
        with open(domain) as domain_file, open(gittree) as gittree_file:
            scm.incremental_import(domain_file, gittree_file)

    def setUp(self):
        '''import initial data'''
        self.import_scm('domain.txt', 'gittree.txt')

    def test_init(self):
        ''' test setup is right '''
        domains = Domain.objects.all().order_by('name')
        # check domain count
        self.assertEqual(len(domains), len(self.sources))

        for i, domain in enumerate(domains):
            self.assertEqual(self.sources[i], domains[i].name)

    def test_add(self):
        ''' test domain add '''
        ref_domains = copy.deepcopy(self.sources)
        ref_domains.append('Automotive')
        ref_domains.sort()
        self.import_scm('domain_add.txt', 'gittree.txt')

        domains = Domain.objects.all().order_by('name')
        self.assertEqual(len(domains), len(ref_domains))
        for i, domain in enumerate(domains):
            self.assertEqual(ref_domains[i], domains[i].name)

    def test_delete(self):
        ''' test domain delete '''
        ref_domains = copy.deepcopy(self.sources)
        ref_domains.remove('App Framework')
        ref_domains.sort()
        self.import_scm('domain_delete.txt', 'gittree.txt')

        domains = Domain.objects.all().order_by('name')
        self.assertEqual(len(domains), len(ref_domains))
        for i, domain in enumerate(domains):
            self.assertEqual(ref_domains[i], domains[i].name)
