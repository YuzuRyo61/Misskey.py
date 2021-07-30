import pytest
import requests

from misskey import Misskey

TEST_HOST = 'http://localhost:3000'


@pytest.fixture(scope='session', autouse=True)
def fixture_session():
    res_admin = requests.post(
        f'{TEST_HOST}/api/admin/accounts/create',
        json={
            'username': 'administrator',
            'password': 'administrator_pass',
        }
    )
    res_admin.raise_for_status()

    res_user = requests.post(
        f'{TEST_HOST}/api/signup',
        json={
            'username': 'user',
            'password': 'user_pass',
        }
    )
    res_user.raise_for_status()

    yield res_admin.json()['token'], res_user.json()['token']


@pytest.fixture()
def mk_cli_anon() -> Misskey:
    return Misskey(TEST_HOST)


@pytest.fixture()
def mk_cli_admin(fixture_session: tuple) -> Misskey:
    return Misskey(TEST_HOST, i=fixture_session[0])


@pytest.fixture()
def mk_cli_user(fixture_session: tuple) -> Misskey:
    return Misskey(TEST_HOST, i=fixture_session[1])


@pytest.fixture()
def mk_admin_token(fixture_session: tuple) -> str:
    return fixture_session[0]


@pytest.fixture()
def mk_user_token(fixture_session: tuple) -> str:
    return fixture_session[1]


@pytest.fixture()
def mk_user_new_note(mk_cli_user: Misskey):
    new_note = mk_cli_user.notes_create(
        text='Unit test message'
    )
    assert type(new_note) == dict
    yield new_note['createdNote']['id']

    is_deleted = mk_cli_user.notes_delete(new_note['createdNote']['id'])
    assert type(is_deleted) == bool
    assert is_deleted
