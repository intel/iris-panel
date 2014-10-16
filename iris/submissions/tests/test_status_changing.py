#pylint: skip-file
from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (
    BuildGroup, Submission,
    )


class StatusTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products', 'submissions']
    url = '/api/submissions/events/%s/'

    def login(self, user='robot', pwd='robot'):
        assert self.client.login(username=user, password=pwd)

    def test_package_failed(self):
        """
        One package succeed and the other failed, then submission status will be "Package Failed"
        """
        gitpath = 'framework/system/dlog'
        tag = 'submit/trunk/yyyy-mm-dd'
        project = 'home:prerelease:tizen:ivi:submit:trunk:01'
        self.login()
        self.client.post(self.url % 'submitted', {
                'gitpath': gitpath,
                'tag': tag,
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.client.post(self.url % 'pre_created', {
                'gitpath': gitpath,
                'tag': tag,
                'product': 'Tizen:IVI',
                'project': project,
                })

        self.client.post(self.url % 'package_built', {
                'name': 'dlog-api',
                'repo': 'standard',
                'arch': 'armv7el',
                'project': project,
                'status': 'OBS_BUILD_FAIL',
                'repo_server': 'http://build.server',
                })

        self.client.post(self.url % 'package_built', {
                'name': 'dlog',
                'repo': 'standard',
                'arch': 'i586',
                'project': project,
                'status': 'OBS_BUILD_SUCCESS',
                'repo_server': 'http://build.server',
                })

        group = BuildGroup.objects.get(name=project)
        submission = Submission.objects.get(
            name=tag, gittree__gitpath=gitpath)
        self.assertEquals('15_PKGFAILED', group.status)
        self.assertEquals('15_PKGFAILED', submission.status)


    def test_image_failed(self):
        gitpath = 'framework/system/dlog'
        tag = 'submit/trunk/yyyy-mm-dd'
        project = 'home:prerelease:tizen:ivi:submit:trunk:01'
        self.login()
        self.client.post(self.url % 'submitted', {
                'gitpath': gitpath,
                'tag': tag,
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.client.post(self.url % 'pre_created', {
                'gitpath': gitpath,
                'tag': tag,
                'product': 'Tizen:IVI',
                'project': project,
                })

        self.client.post(self.url % 'image_building', {
                'name': 'image1',
                'project': project,
                'repo': 'standard',
                })

        self.client.post(self.url % 'image_building', {
                'name': 'image2',
                'project': project,
                'repo': 'standard',
                })

        self.client.post(self.url % 'image_created', {
                'name': 'image1',
                'project': project,
                'status': 'success',
                'url': 'http://url1.com',
                })

        self.client.post(self.url % 'image_created', {
                'name': 'image2',
                'project': project,
                'status': 'failed',
                'url': 'http://url2.com',
                })

        group = BuildGroup.objects.get(name=project)
        submission = Submission.objects.get(
            name=tag, gittree__gitpath=gitpath)
        self.assertEquals('25_IMGFAILED', group.status)
        self.assertEquals('25_IMGFAILED', submission.status)
