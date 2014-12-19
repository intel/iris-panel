# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
#pylint: skip-file
import os
import ast

from django.test import TestCase


def parse_events_log(stream):
    for line in stream:
        _, path, param = line.rstrip().split('|')
        typ = path.rstrip('/').split('/')[-1]
        data = dict(ast.literal_eval(param))
        yield typ, data


class SmokingTest(TestCase):

    fixtures = ['users', 'domains', 'subdomains', 'gittrees', 'products']

    def url(self, typ):
        return '/api/submissions/events/%s/' % typ

    def _get_events(self):
        filename = os.path.join(os.path.dirname(__file__), 'events.log')
        with open(filename) as reader:
            return list(parse_events_log(reader))

    def test(self):
        self.client.login(username='robot', password='robot')
        for i, (typ, data) in enumerate(self._get_events()):
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


def main():
    import argparse
    import sys
    from common.iris_rest_client import IrisRestClient as Client

    p = argparse.ArgumentParser()
    p.add_argument('server')
    p.add_argument('--username', '-u')
    p.add_argument('--password', '-p')
    args = p.parse_args()

    c = Client(args.server, args.username, args.password)
    for typ, data in parse_events_log(sys.stdin):
        c.publish_event(typ, data)


if __name__ == '__main__':
    main()
