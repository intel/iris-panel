# This file is part of IRIS: Infrastructure and Release Information System
#
# Copyright (C) 2013-2015 Intel Corporation
#
# IRIS is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.0 as published by the Free Software Foundation.
#pylint: disable=missing-docstring,invalid-name

from iris.etl.parser import UserCache


def test_merge_name_and_full():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('David Bowie <david.bowie@i.com>')

    assert uc.all() == [
        {'first_name': 'David',
         'last_name': 'Bowie',
         'email': 'david.bowie@i.com'}]


def test_merge_full_and_email():
    uc = UserCache()
    uc.update('David Bowie <david.bowie@i.com>')
    uc.update('david.bowie@i.com')

    assert uc.all() == [
        {'first_name': 'David',
         'last_name': 'Bowie',
         'email': 'david.bowie@i.com'}]


def test_merge_3_forms():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('david.bowie@i.com')
    uc.update('David Bowie <david.bowie@i.com>')

    assert uc.all() == [
        {'first_name': 'David',
         'last_name': 'Bowie',
         'email': 'david.bowie@i.com'}]


def test_cannot_merge_name_and_email():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('david.bowie@i.com')

    assert uc.all() == [
        {'first_name': '',
         'last_name': '',
         'email': 'david.bowie@i.com'},
        ]


def test_cannot_merge_diff_names():
    uc = UserCache()
    uc.update('Eric Clapton')
    uc.update('Eric Johnson')

    assert uc.all() == []


def test_cannot_merge_diff_emails():
    uc = UserCache()
    uc.update('joe@satriani.com')
    uc.update('steve@vai.com')

    assert uc.all() == [
        {'first_name': '', 'last_name': '', 'email': 'joe@satriani.com'},
        {'first_name': '', 'last_name': '', 'email': 'steve@vai.com'},
        ]


def test_different_names_with_the_same_email():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('David Robert Jones <david.bowie@i.com>')
    uc.update('David Bowie <david.bowie@i.com>')
    uc.update('David Robert Jones')
    uc.update('Bowie David <david.bowie@i.com>')

    users = uc.all()
    assert len(users) == 1 and users[0]['email'] == 'david.bowie@i.com'


def test_get_by_name():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('David Bowie <david.bowie@i.com>')

    assert uc.get('David Bowie') == {
        'first_name': 'David',
        'last_name': 'Bowie',
        'email': 'david.bowie@i.com'}


def test_get_by_email():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('David Robert Jones <david.bowie@i.com>')
    uc.update('David Bowie <david.bowie@i.com>')
    uc.update('david.bowie@i.com')

    assert uc.get('david.bowie@i.com')['email'] == 'david.bowie@i.com'


def test_get_by_full():
    uc = UserCache()
    uc.update('david.bowie@i.com')
    uc.update('David Bowie <david.bowie@i.com>')

    assert uc.get('David Bowie <david.bowie@i.com>') == {
        'first_name': 'David',
        'last_name': 'Bowie',
        'email': 'david.bowie@i.com'}


def test_user_without_email_will_be_ignored():
    uc = UserCache()
    uc.update('Brian May')
    uc.update('Roger Taylor')
    uc.update('Freddie Mercury <freddie@queen.com>')

    assert uc.get('Brian May') is None
    assert uc.all() == [
        {'first_name': 'Freddie',
         'last_name': 'Mercury',
         'email': 'freddie@queen.com'}
        ]
