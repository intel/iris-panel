#pylint: skip-file

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

    assert sorted(uc.all(), key=lambda x: x['email']) == [
        {'first_name': 'David',
         'last_name': 'Bowie',
         'email': ''},
        {'first_name': '',
         'last_name': '',
         'email': 'david.bowie@i.com'},
        ]


def test_different_names_with_the_same_email():
    uc = UserCache()
    uc.update('David Bowie')
    uc.update('David Robert Jones <david.bowie@i.com>')
    uc.update('David Bowie <david.bowie@i.com>')
    uc.update('David Robert Jones')

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
