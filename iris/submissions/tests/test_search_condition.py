# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
#pylint: skip-file
from django.test import TestCase
from django.core.exceptions import ValidationError

from iris.submissions.views.read import parse_query_string as parse


class SearchConditionTest(TestCase):

    def test_one_value(self):
        self.assertEquals({
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse('submit/tizen_ivi/20141210.778899'))

    def test_two_value(self):
        self.assertEquals(None, parse('submit tizen_common'))

    def test_one_value_one_status_pair(self):
        self.assertEquals({
            'status': 'opened',
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse('status:opened submit/tizen_ivi/20141210.778899'))

    def test_one_value_one_wrong_status_pair(self):
        self.assertEquals(None, parse('status:building submit/tizen_ivi/20141210.778899'))

    def test_one_value_one_owner_pair(self):
        self.assertEquals({
            'owner': 'lily@xx.com',
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse('owner:lily@xx.com submit/tizen_ivi/20141210.778899'))

    def test_one_value_one_gittree_pair(self):
        self.assertEquals({
            'gittree': 'platform/upstream/wayland',
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse('gittree:platform/upstream/wayland  submit/tizen_ivi/20141210.778899'))

    def test_one_value_one_name_pair(self):
        self.assertEquals({
            'name': 'submit/tizen_ivi/20141210.778899',
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse('name:submit/tizen_ivi/20141210.778899 submit/tizen_ivi/20141210.778899'))

    def test_one_value_one_wrong_key_pair(self):
        self.assertEquals(None, parse('product:tizen_common submit/tizen_ivi/20141210.778899'))

    def test_one_value_all_pairs(self):
        self.assertEquals({
            'name': 'submit/tizen/20141208.164610',
            'status': 'accepted',
            'owner': 'lily@xx.com',
            'gittree': 'platform/upstream/wayland',
            'query': 'submit/tizen_ivi/20141210.778899'
        }, parse(
            'name:submit/tizen/20141208.164610 '
            'status:accepted owner:lily@xx.com '
            'gittree:platform/upstream/wayland '
            'submit/tizen_ivi/20141210.778899'))
