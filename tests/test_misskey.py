import uuid

import pytest

from urllib.parse import urlparse

import requests

from misskey import Misskey
from misskey.exceptions import (
    MisskeyAuthorizeFailedException,
    MisskeyAPIException,
)

from .conftest import TEST_HOST


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


@pytest.mark.parametrize('host', [
    'http://unknown-host',
    'unknown-host',
])
def test_should_connect_error_in_init(host: str):
    with pytest.raises(requests.exceptions.ConnectionError):
        Misskey(host)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, '')
])
def test_should_token_error_in_init(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        Misskey(host, i=TEST_HOST)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, ''),
])
def test_should_token_error_in_setter(host: str, token: str):
    with pytest.raises(MisskeyAuthorizeFailedException):
        mk = Misskey(host)
        mk.token = token


def test_address_should_be_same(mk_cli_anon: Misskey):
    host_url = urlparse(TEST_HOST)
    assert mk_cli_anon.address == host_url.netloc


def test_token_should_be_valid(mk_cli_user: Misskey, mk_user_token: str):
    assert mk_cli_user.token == mk_user_token


def test_token_should_be_settable(mk_user_token: str):
    mk = Misskey(TEST_HOST)
    mk.token = mk_user_token


def test_should_success_i(mk_cli_user: Misskey):
    res = mk_cli_user.i()
    assert type(res) == dict


def test_should_fail_i(mk_cli_anon: Misskey):
    with pytest.raises(MisskeyAPIException) as e:
        mk_cli_anon.i()

    assert type(e.value.code) == str
    assert type(e.value.message) == str
    assert type(e.value.id) == uuid.UUID or type(e.value.id) == str
