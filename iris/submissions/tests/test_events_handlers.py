# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
#pylint: skip-file
from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (
    Domain, SubDomain, GitTree, Product,
    Submission, Snapshot, BuildGroup
    )


class EventHandlerTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products', 'submissions']
    url = '/api/submissions/events/%s/'

    def login(self, user='robot', pwd='robot'):
        assert self.client.login(username=user, password=pwd)

    def test_post_required(self):
        self.login()
        r = self.client.get(self.url % 'submitted')
        self.assertEquals(405, r.status_code)

    def test_login_required(self):
        r = self.client.post(self.url % 'submitted')
        self.assertEquals(403, r.status_code)

    def test_permission_required(self):
        self.login('alice', 'alice')
        r = self.client.post(self.url % 'submitted', {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/yyyy-mm-dd',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.assertEquals(403, r.status_code)

    def test_missing_parameter(self):
        self.login()
        r = self.client.post(self.url % 'submitted')
        self.assertEquals(406, r.status_code)

    def test_submitted(self):
        self.login()
        r = self.client.post(self.url % 'submitted', {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/yyyy-mm-dd',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.assertEquals(201, r.status_code)
        Submission.objects.get(name='submit/trunk/yyyy-mm-dd')

    def test_pre_created(self):
        self.login()
        r = self.client.post(self.url % 'pre_created', {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/01',
                'product': 'Tizen:IVI',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(201, r.status_code)

    def test_pre_created_bad_submission(self):
        self.login()
        r = self.client.post(self.url % 'pre_created', {
                'gitpath': 'does/not/exist',
                'tag': 'does/not/exist',
                'product': 'Tizen:IVI',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(406, r.status_code)

    def test_pre_created_un_exist_product(self):
        self.login()
        r = self.client.post(self.url % 'pre_created', {
                'gitpath': 'framework/system/dlog',
                'tag': 'submit/trunk/01',
                'product': 'Tizen:Test',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:01',
                })
        self.assertEquals(201, r.status_code)
        Product.objects.get(name="Tizen:Test")

    def test_pre_created_with_same_product_in_one_project(self):
        gittrees = ['platform/upstream/bluez', 'framework/system/dlog']
        for gittree in gittrees:
            self.login()
            self.client.post(self.url % 'submitted', {
                'gitpath': gittree,
                'tag': 'submit/trunk/product-same',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
            r = self.client.post(self.url % 'pre_created', {
                'gitpath': gittree,
                'tag': 'submit/trunk/product-same',
                'product': 'Tizen:IVI',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:same',
                })
        self.assertEquals(201, r.status_code)

    def test_pre_created_with_different_product_in_one_project(self):
        gittrees = ['platform/upstream/bluez', 'framework/system/dlog']
        for gittree in gittrees:
            self.login()
            self.client.post(self.url % 'submitted', {
                'gitpath': gittree,
                'tag': 'submit/trunk/product-different',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.client.post(self.url % 'pre_created', {
           'gitpath': gittrees[0],
           'tag': 'submit/trunk/product-different',
           'product': 'Tizen:IVI',
           'project': 'home:prerelease:tizen:ivi:submit:trunk:different',
        })

        r = self.client.post(self.url % 'pre_created', {
           'gitpath': gittrees[0],
           'tag': 'submit/trunk/product-different',
           'product': 'Tizen:Common',
           'project': 'home:prerelease:tizen:ivi:submit:trunk:different',
        })
        self.assertEquals(406, r.status_code)

    def test_pre_created_with_different_product_in_different_project(self):
        gittrees = ['platform/upstream/bluez', 'framework/system/dlog']
        for gittree in gittrees:
            self.login()
            self.client.post(self.url % 'submitted', {
                'gitpath': gittree,
                'tag': 'submit/trunk/product-different',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.client.post(self.url % 'pre_created', {
           'gitpath': gittrees[0],
           'tag': 'submit/trunk/product-different',
           'product': 'Tizen:IVI',
           'project': 'home:prerelease:tizen:ivi:submit:trunk:different-1',
        })

        r = self.client.post(self.url % 'pre_created', {
           'gitpath': gittrees[0],
           'tag': 'submit/trunk/product-different',
           'product': 'Tizen:Common',
           'project': 'home:prerelease:tizen:ivi:submit:trunk:different-2',
        })
        self.assertEquals(201, r.status_code)

    def test_package_built_succeeded(self):
        self.login()
        r = self.client.post(self.url % 'package_built', {
                'name': 'dlog',
                'repo': 'standard',
                'arch': 'i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'OBS_BUILD_SUCCESS',
                'repo_server': 'http://build.server',
                })
        self.assertEquals(200, r.status_code)

    def test_package_built_failed(self):
        self.login()
        r = self.client.post(self.url % 'package_built', {
                'name': 'dlog',
                'repo': 'standard',
                'arch': 'armv7el',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'OBS_BUILD_FAIL',
                'repo_server': 'http://build.server',
                })
        self.assertEquals(200, r.status_code)

    def test_image_building(self):
        self.login()
        r = self.client.post(self.url % 'image_building', {
                'name': 'ivi-mbr-i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'repo': 'atom',
                })
        self.assertEquals(200, r.status_code)

    def test_image_building_bad_project(self):
        self.login()
        r = self.client.post(self.url % 'image_building', {
                'name': 'ivi-mbr-i586',
                'project': 'doesnotexist',
                'repo': 'atom',
                })
        self.assertEquals(406, r.status_code)

    def test_image_created(self):
        self.login()
        r = self.client.post(self.url % 'image_created', {
                'name': 'ivi-mbr-x64',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(200, r.status_code)

    def test_image_created_image_doesnot_exist(self):
        self.login()
        r = self.client.post(self.url % 'image_created', {
                'name': 'ivi-mbr-i586',
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(406, r.status_code)

    def test_image_created_project_doesnot_exist(self):
        self.login()
        r = self.client.post(self.url % 'image_created', {
                'name': 'ivi-mbr-i586',
                'project': 'doesnt exist',
                'status': 'success',
                'url': 'http://url.to.image',
                'log': 'http://url.to.image.log',
                })
        self.assertEquals(406, r.status_code)

    def test_repa_accepted(self):
        self.login()
        r = self.client.post(self.url % 'repa_action', {
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'accepted',
                'who': 'someone@tizen.org',
                'reason': 'Good!',
                })
        self.assertEquals(200, r.status_code)

    def test_repa_rejected(self):
        self.login()
        r = self.client.post(self.url % 'repa_action', {
                'project': 'home:prerelease:tizen:ivi:submit:trunk:02',
                'status': 'declined',
                'who': 'someone@tizen.org',
                'reason': "Errors found in QA tests",
                })
        self.assertEquals(200, r.status_code)

    def test_snapshot_start(self):
        self.login()
        r = self.client.post(self.url % 'snapshot_start', {
                'project': 'Tizen:IVI',
                'buildid': 'tizen-ivi_20141107.5',
                'started_time': '2014-10-30 13:34:15'

                })
        self.assertEquals(200, r.status_code)
        Snapshot.objects.get(product__name='Tizen:IVI',
                            buildid='tizen-ivi_20141107.5')

    def test_snapshot_finish(self):
        self.login()
        r = self.client.post(self.url % 'snapshot_finish', {
                'project': 'Tizen:IVI',
                'buildid': 'tizen-ivi_20141023.5',
                'finished_time': '2014-10-23 11:30:02',
                'url': 'http://url.to.snapshot'
                })
        self.assertEquals(200, r.status_code)

        snap = Snapshot.objects.get(product__name='Tizen:IVI',
                                    buildid='tizen-ivi_20141023.5')
        # there are two accepted submissions, but only one submission is
        # operated before this snapshot starts
        self.assertEqual(BuildGroup.objects.filter(snapshot=snap).count(), 1)

        r = self.client.post(self.url % 'snapshot_finish', {
                'project': 'Tizen:IVI',
                'buildid': 'tizen-ivi_20141024.5',
                'finished_time': '2014-10-24 11:30:02',
                'url': 'http://url.to.snapshot'
                })
        self.assertEquals(200, r.status_code)
        snap = Snapshot.objects.get(product__name='Tizen:IVI',
                                    buildid='tizen-ivi_20141024.5')
        # there are two accepted submissions, and both of them are operated
        # before this snapshot, but one of them are set to the previous snapshot,
        # so here there is still only one submission for the snapshot
        self.assertEqual(BuildGroup.objects.filter(snapshot=snap).count(), 1)

    def test_snapshot_release(self):
        self.login()
        r = self.client.post(self.url % 'snapshot_release', {
                'project': 'Tizen:IVI',
                'buildid': 'tizen-ivi_20141023.5',
                'release_type': 'daily',
                'url': 'http://url.to.daily/'
                })
        self.assertEquals(200, r.status_code)
        Snapshot.objects.get(product__name='Tizen:IVI',
                             buildid='tizen-ivi_20141023.5',
                             daily_url='http://url.to.daily/')

        r = self.client.post(self.url % 'snapshot_release', {
                'project': 'Tizen:IVI',
                'buildid': 'tizen-ivi_20141023.5',
                'release_type': 'weekly',
                'url': 'http://url.to.weekly/'
                })
        self.assertEquals(200, r.status_code)
        Snapshot.objects.get(product__name='Tizen:IVI',
                             buildid='tizen-ivi_20141023.5',
                             daily_url='http://url.to.daily/',
                             weekly_url='http://url.to.weekly/')
