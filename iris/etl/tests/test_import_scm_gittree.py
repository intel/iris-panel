# -*- encoding: utf-8 -*-
# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
'''
This module is used to test import scm data module: iris/etl/scm.py
'''
#pylint: disable=missing-docstring,no-member,invalid-name

import unittest

from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain, GitTree, License, GitTreeRole
from iris.etl.scm import from_string, ROLES


class GitTreeTest(unittest.TestCase):

    def tearDown(self):
        GitTree.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()

    def test_add_one_GitTree(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: dapt/alsa
        D: System / Alarm
        ''')
        self.assertEqual(
            ['dapt/alsa'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm')])

    def test_add_one_GitTree_with_empty_domain(self):
        from_string('''
        T: dapt/alsa
        D:
        ''')
        self.assertEqual(
            ['dapt/alsa'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Uncategorized',
                subdomain__domain__name='Uncategorized')])

    def test_add_one_GitTree_without_domain(self):
        from_string('''
        T: dapt/alsa
        ''')
        self.assertEqual(
            ['dapt/alsa'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Uncategorized',
                subdomain__domain__name='Uncategorized')])

    def test_add_one_GitTree_with_domain(self):
        from_string('''
        D: System

        T: dapt/alsa
        D: System
        ''')
        self.assertEqual(
            ['dapt/alsa'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Uncategorized',
                subdomain__domain__name='System')])

    def test_gitpath_include_colon(self):
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: dapt/alsa:sde
        D: System / Alarm
        ''')
        self.assertEqual(
            ['dapt/alsa:sde'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm')])

    def test_add_gittree_dont_delete_others(self):
        from_string('''
         D: System

         D: System / Alarm
         N: System

         T: dapt/alsa
         D: System / Alarm
         ''')
        from_string('''
         D: System

         D: System / Alarm
         N: System

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
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System

        T: adaptation/face-engine
        D: System / Alarm

        T: adaptation/alsa-scen
        D: System / Alarm

        T: apps/core/preloaded/email
        D: System / Call
        ''')
        self.assertEqual([
            'adaptation/alsa-scen',
            'adaptation/face-engine',
            'apps/core/preloaded/email'
        ], [
            g.gitpath for g in GitTree.objects.all().order_by('gitpath')
        ])

    def test_delete_gittree(self):
        ''' delete gitree: ad/alsa '''
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System

        T: ad/face
        D: System / Alarm

        T: ad/alsa
        D: System / Alarm

        T: apps/core/preloaded/email
        D: System / Call
        ''')

        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System

        T: ad/face
        D: System / Alarm

        T: apps/core/preloaded/email
        D: System / Call
        ''')

        self.assertEqual([
            'ad/face',
            'apps/core/preloaded/email'
        ], [
            g.gitpath for g in GitTree.objects.all().order_by('gitpath')
        ])
        self.assertEqual(
            ['ad/face'],
            [g.gitpath for g in GitTree.objects.filter(
                subdomain__name='Alarm')])
        self.assertEqual(
            ['apps/core/preloaded/email'],
            [g.gitpath for g in GitTree.objects.filter(subdomain__name='Call')])

    def test_update_GitTree(self):
        '''Change gitree's subdomain from "System / Alarm" to "System / Call" '''
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/alsa-scenario-scn-data-0-base
        D: System / Alarm
        ''')
        from_string('''
        D: System

        D: System / Alarm
        N: System

        D: System / Call
        N: System

        T: adaptation/alsa-scenario-scn-data-0-base
        D: System / Call
        ''')
        self.assertEqual(
            [],
            [g.gitpath for g in GitTree.objects.filter(subdomain__name='Alarm')])
        self.assertEqual(
            ['adaptation/alsa-scenario-scn-data-0-base'],
            [g.gitpath for g in GitTree.objects.filter(subdomain__name='Call')])


class TestGitTreeRole(unittest.TestCase):
    def tearDown(self):
        GitTreeRole.objects.all().delete()
        GitTree.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()
        User.objects.all().delete()

    def test_add_gittree_maintainer(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        M: Mike <mike@i.com>
        ''')
        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role="MAINTAINER").user_set.all()])

    def test_add_two_gittree_reviewers(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        R: Mike <mike@i.com>
        R: Lucy David <lucy.david@inher.com>
        ''')
        self.assertEqual(
            ['Lucy', 'Mike'],
            [i.first_name.encode('utf8') for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b',
                role='REVIEWER').user_set.all().order_by('first_name')])

    def test_delete_integrators(self):
        ''' delete integrator: Mike <mike@i.com> '''

        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        I: Mike <mike@i.com>
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''')
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        I: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        ''')
        self.assertEqual(
            ['lily.edurd@inher.com', 'lucy.david@inher.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b',
                role='INTEGRATOR').user_set.all().order_by('email')])

    def test_delete_all_roles(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        R: Mike <mike@i.com>
        A: Lucy David <lucy.david@inher.com>
        I: <lily.edurd@inher.com>
        M: <tom.edurd@inher.com>
        ''')
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        ''')
        for role in ROLES:
            self.assertEqual(
                [],
                [r.role for r in GitTreeRole.objects.filter(
                    gittree__gitpath='a/b',
                    role=role)])

    def test_update_architectures(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        A: Mike <mike@i.com>
        ''')
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        A: Mike Frédéric <mike@i.com>
        ''')

        self.assertEqual(
            ['Frédéric'],
            [i.last_name.encode('utf8') for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role='ARCHITECT').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_add_same_user_in_different_gittree(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        D: Appframework

        D: Appframework / Gallery
        N: Appframework

        T: a/b
        D: System / Clock
        A: Mike <mike@i.com>

        T: c/d
        D: Appframework / Gallery
        M: Mike <mike@i.com>
        ''')

        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role='ARCHITECT').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='c/d', role='MAINTAINER').user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [u.email for u in User.objects.all()])

    def test_roles_transform(self):
        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        A: Mike <mike@i.com>
        M: Lily David <lily.david@hello.com>
        I: <lucy.chung@wel.com>
        R: Tom Frédéric <tom.adwel@hello.com>
        ''')

        from_string('''
        D: System

        D: System / Clock
        N: System

        T: a/b
        D: System / Clock
        M: Mike <mike@i.com>
        R: Lily David <lily.david@hello.com>
        A: <lucy.chung@wel.com>
        I: Tom Frédéric <tom.adwel@hello.com>
        ''')
        self.assertEqual(
            ['lucy.chung@wel.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role="ARCHITECT").user_set.all()])
        self.assertEqual(
            ['lily.david@hello.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role="REVIEWER").user_set.all()])
        self.assertEqual(
            ['mike@i.com'],
            [i.email for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role="MAINTAINER").user_set.all()])
        self.assertEqual(
            ['Frédéric'],
            [i.last_name.encode('utf8') for i in GitTreeRole.objects.get(
                gittree__gitpath='a/b', role="INTEGRATOR").user_set.all()])
        self.assertEqual([
            'lily.david@hello.com',
            'lucy.chung@wel.com',
            'mike@i.com',
            'tom.adwel@hello.com'
        ], [
            u.email for u in User.objects.all().order_by('email')
        ])

class GitTreeLicenseTest(unittest.TestCase):

    def tearDown(self):
        License.objects.all().delete()
        GitTree.objects.all().delete()
        SubDomain.objects.all().delete()
        Domain.objects.all().delete()

    def test_add_one_license_for_gittree(self):
        License.objects.create(shortname='BSD-2-Clause')
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: dapt/alsa
        D: System / Alarm
        L: BSD-2-Clause
        ''')
        self.assertEqual(
            ['BSD-2-Clause'],
            [l.shortname for l in License.objects.filter(
                gittree__gitpath='dapt/alsa')])

    def test_add_three_licenses_for_gittree(self):
        License.objects.bulk_create([
            License(shortname='BSD-2-Clause'),
            License(shortname='CC-BY-NC-2.5'),
            License(shortname='Epinions')
        ])
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/face-engine
        D: System / Alarm
        L: BSD-2-Clause
        L: CC-BY-NC-2.5
        L: Epinions
        ''')
        self.assertEqual(
            ['BSD-2-Clause', 'CC-BY-NC-2.5', 'Epinions'],
            [l.shortname for l in License.objects.filter(
                gittree__gitpath='adaptation/face-engine')])

    def test_delete_license_for_gittree(self):
        ''' left one license '''
        License.objects.bulk_create([
            License(shortname='BSD-2-Clause'),
            License(shortname='CC-BY-NC-2.5'),
            License(shortname='Epinions')
        ])
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/face-engine
        D: System / Alarm
        L: BSD-2-Clause
        L: CC-BY-NC-2.5
        L: Epinions
        ''')
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/face-engine
        D: System / Alarm
        L: Epinions
        ''')

        self.assertEqual(
            ['Epinions'],
            [l.shortname for l in License.objects.filter(
                gittree__gitpath='adaptation/face-engine')])

    def test_delete_all_license_for_gittree(self):
        License.objects.bulk_create([
            License(shortname='BSD-2-Clause'),
            License(shortname='CC-BY-NC-2.5'),
            License(shortname='Epinions')
        ])
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/face-engine
        D: System / Alarm
        L: BSD-2-Clause
        L: CC-BY-NC-2.5
        L: Epinions
        ''')
        from_string('''
        D: System

        D: System / Alarm
        N: System

        T: adaptation/face-engine
        D: System / Alarm
        ''')
        self.assertEqual(
            [],
            [l.shortname for l in License.objects.filter(
                gittree__gitpath='adaptation/face-engine')])
