import time

import pytest
import requests

from misskey import Misskey

TEST_HOST = 'http://localhost:3000'


@pytest.fixture(scope='session', autouse=True)
def fixture_session():
    admin_cred = {
        'username': 'administrator',
        'password': 'administrator_pass',
    }
    user_cred = {
        'username': 'user',
        'password': 'user_pass',
    }

    res_admin = requests.post(
        f'{TEST_HOST}/api/admin/accounts/create',
        json=admin_cred,
    )
    try:
        res_admin.raise_for_status()
    except requests.HTTPError:
        res_admin_signin = requests.post(
            f'{TEST_HOST}/api/signin',
            json=admin_cred,
        )
        res_admin_signin.raise_for_status()
        token_admin = res_admin_signin.json()['i']
    else:
        token_admin = res_admin.json()['token']

    res_user = requests.post(
        f'{TEST_HOST}/api/signup',
        json=user_cred,
    )
    try:
        res_user.raise_for_status()
    except requests.HTTPError:
        res_user_signin = requests.post(
            f'{TEST_HOST}/api/signin',
            json=user_cred,
        )
        res_user_signin.raise_for_status()
        token_user = res_user_signin.json()['i']
    else:
        token_user = res_user.json()['token']

    yield token_admin, token_user


@pytest.fixture(scope='session')
def mk_cli_anon() -> Misskey:
    return Misskey(TEST_HOST)


@pytest.fixture(scope='session')
def mk_cli_admin(fixture_session: tuple) -> Misskey:
    return Misskey(TEST_HOST, i=fixture_session[0])


@pytest.fixture(scope='session')
def mk_cli_user(fixture_session: tuple) -> Misskey:
    return Misskey(TEST_HOST, i=fixture_session[1])


@pytest.fixture(scope='session')
def mk_admin_token(fixture_session: tuple) -> str:
    return fixture_session[0]


@pytest.fixture(scope='session')
def mk_user_token(fixture_session: tuple) -> str:
    return fixture_session[1]


@pytest.fixture(scope='session')
def mk_admin_id(mk_cli_admin: Misskey) -> str:
    return mk_cli_admin.i()['id']


@pytest.fixture(scope='session')
def mk_user_id(mk_cli_user: Misskey) -> str:
    return mk_cli_user.i()['id']


@pytest.fixture()
def mk_admin_new_note(mk_cli_admin: Misskey):
    new_note = mk_cli_admin.notes_create(
        text='Unit test message'
    )
    assert type(new_note) == dict
    yield new_note['createdNote']['id']

    is_deleted = mk_cli_admin.notes_delete(new_note['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted


# Avoid rate limit
# https://stackoverflow.com/a/66974375
@pytest.fixture(autouse=True)
def slow_down_tests():
    yield
    time.sleep(1)
