#pylint: skip-file
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from iris.core.models import Domain, SubDomain, GitTree, Submission


class EventHandlerTest(TestCase):

    user, pwd, email = 'admin', 'admin', 'admin@localhost'

    def setUp(self):
        User.objects.create_superuser(self.user, self.email, self.pwd)
        d = Domain.objects.create(name='System')
        s = SubDomain.objects.create(name='Logging', domain=d)
        t = GitTree.objects.create(gitpath='framework/system/dlog', subdomain=s)

    def login(self):
        assert self.client.login(username=self.user, password=self.pwd)

    def test_post_required(self):
        url = reverse('event_submitted')
        self.login()
        r = self.client.get(url)
        self.assertEquals(405, r.status_code)

    def test_login_required(self):
        url = reverse('event_submitted')
        r = self.client.post(url)
        self.assertEquals(403, r.status_code)

    def test_missing_parameter(self):
        url = reverse('event_submitted')
        self.login()
        r = self.client.post(url)
        self.assertEquals(406, r.status_code)

    def test_submitted(self):
        url = reverse('event_submitted')
        self.login()
        r = self.client.post(url, {
                'gitpath': '/framework/system/dlog',
                'tag': 'submit/trunk/yyyy-mm-dd',
                'commit_id': 'sha1',
                'submitter_email': 'someone@localhost',
                })
        self.assertEquals(201, r.status_code)

        Submission.objects.get(name='submit/trunk/yyyy-mm-dd')

