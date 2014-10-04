#pylint: skip-file
import os
import ast

from django.test import TestCase


class SmokingTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products']

    def url(self, typ):
        return '/api/submissions/events/%s/' % typ

    def _parse_events_log(self):
        filename = os.path.join(os.path.dirname(__file__), 'events.log')
        events = []
        with open(filename) as reader:
            for line in reader:
                _, path, param = line.rstrip().split('|')
                typ = path.rstrip('/').split('/')[-1]
                data = dict(ast.literal_eval(param))
                events.append((typ, data))
        return events

    def test(self):
        self.client.login(username='robot', password='robot')
        for i, (typ, data) in enumerate(self._parse_events_log()):
            r = self.client.post(self.url(typ), data)
            self.assertTrue(
                r.status_code >= 200 and r.status_code < 300,
                "[Line:%d] "
                "[Respnose: code=%s, conten=%s] "
                "[Request: typ=%s, data=%s]" % (
                    i+1,
                    r.status_code, r.content,
                    typ, data
                    ))
