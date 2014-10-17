#pylint: skip-file
from django.test import TestCase
from django.contrib.auth.models import User

from iris.core.models import (
    BuildGroup, Submission,
    )


class StatusTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products', 'submissions']
    url = '/api/submissions/events/%s/'

    gitpath = 'framework/system/dlog'
    tag = 'submit/trunk/yyyy-mm-dd'
    project = 'home:prerelease:tizen:ivi:submit:trunk:01'

    def setUp(self):
        """
        Create a submission tag and pre-release project
        """
        self.login()
        self.client.post(self.url % 'submitted', {
                'gitpath': self.gitpath,
                'tag': self.tag,
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.client.post(self.url % 'pre_created', {
                'gitpath': self.gitpath,
                'tag': self.tag,
                'product': 'Tizen:IVI',
                'project': self.project,
                })

    def login(self, user='robot', pwd='robot'):
        assert self.client.login(username=user, password=pwd)

    def package_built(self, package, is_success):
        """
        Send a package_built event for `package` with status `is_success`
        """
        self.client.post(self.url % 'package_built', {
                'name': package,
                'repo': 'standard',
                'arch': 'armv7el',
                'project': self.project,
                'status': 'OBS_BUILD_SUCCESS' if is_success else 'OBS_BUILD_FAIL',
                'repo_server': 'http://build.server',
                })

    def image_building(self, image):
        """
        Send a image_building event for `image`
        """
        self.client.post(self.url % 'image_building', {
                'name': image,
                'project': self.project,
                'repo': 'standard',
                })

    def image_created(self, image, is_success):
        """
        Send a image_created event for `image` with status `is_success`
        """
        self.client.post(self.url % 'image_created', {
                'name': image,
                'project': self.project,
                'status': 'success' if is_success else 'failed',
                'url': 'http://url1.com',
                })

    @property
    def submission(self):
        return Submission.objects.get(
            name=self.tag, gittree__gitpath=self.gitpath)

    def test_package_failed(self):
        """
        One package succeed and the other failed, then submission status will be "Package Failed"
        """
        self.package_built('dlog-api', False)
        self.package_built('dlog', True)

        self.assertEquals('15_PKGFAILED', self.submission.status)

    def test_image_failed(self):
        self.image_building('image1')
        self.image_building('image2')

        self.image_created('image1', True)
        self.image_created('image2', False)

        self.assertEquals('25_IMGFAILED', self.submission.status)
