# -*- encoding: utf-8 -*-
'''
This module is used to test import scm data module: iris/etl/scm.py
'''

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain, GitTree
from iris.etl import scm

#pylint: skip-file

class GitTreeTest(unittest.TestCase):

    def tearDown(self):
        GitTree.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()

    def test_add_one_GitTree(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System
        ''',
        '''
        T: dapt/alsa
        D: System / Alarm
        ''')
        self.assertEqual(
            ['dapt/alsa'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm')])

    def test_add_gittree_dont_delete_others(self):
        scm.incremental_import_core('''
         D: System

         D: System / Alarm
         N: System
         ''',
         '''
         T: dapt/alsa
         D: System / Alarm
         ''')
        scm.incremental_import_core('''
         D: System

         D: System / Alarm
         N: System
         ''',
         '''
         T: dapt/alsa
         D: System / Alarm

         T: ton/face
         D: System / Alarm
         ''')
        self.assertEqual(
           ['dapt/alsa', 'ton/face'],
           [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm').order_by('gitpath')])

    def test_add_three_gittrees(self):
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''',
        '''
         T: adaptation/face-engine
         D: System / Alarm

         T: adaptation/alsa-scen
         D: System / Alarm

         T: apps/core/preloaded/email
         D: System / Call
        ''')
        self.assertEqual(
            ['adaptation/alsa-scen',
             'adaptation/face-engine',
             'apps/core/preloaded/email'],
            [ g.gitpath for g in GitTree.objects.all().order_by('gitpath')])

    def test_delete_gittree(self):
        ''' delete gitree: ad/alsa '''
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''',
        '''
         T: ad/face
         D: System / Alarm

         T: ad/alsa
         D: System / Alarm

         T: apps/core/preloaded/email
         D: System / Call
        ''')

        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''',
        '''
         T: ad/face
         D: System / Alarm

         T: apps/core/preloaded/email
         D: System / Call
        ''')

        self.assertEqual(
            ['ad/face', 'apps/core/preloaded/email'],
            [g.gitpath for g in GitTree.objects.all().order_by('gitpath')])
        self.assertEqual(
            ['ad/face'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm')])
        self.assertEqual(
            ['apps/core/preloaded/email'],
            [g.gitpath for g in GitTree.objects.filter(subdomain__name='Call')])

    def test_update_GitTree(self):
        '''Change gitree's subdomain from "System / Alarm" to "System / Call" '''
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System
        ''',
        '''
        T: adaptation/alsa-scenario-scn-data-0-base
        D: System / Alarm
        ''')
        scm.incremental_import_core('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System
        ''',
        '''
        T: adaptation/alsa-scenario-scn-data-0-base
        D: System / Call
        ''')
        self.assertEqual(
           [],
           [g.gitpath for g in GitTree.objects.filter(subdomain__name='Alarm')])
        self.assertEqual(
           ['adaptation/alsa-scenario-scn-data-0-base'],
           [g.gitpath for g in GitTree.objects.filter(subdomain__name='Call')])
