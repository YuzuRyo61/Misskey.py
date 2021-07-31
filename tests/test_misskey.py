import datetime
import uuid
from urllib.parse import urlparse

import pytest
import requests

from misskey import (
    Misskey,
    NotificationsType
)
from misskey.exceptions import (
    MisskeyAuthorizeFailedException,
    MisskeyAPIException,
)
from .conftest import TEST_HOST


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


def test_token_should_be_valid(
    mk_cli_user: Misskey,
    mk_user_token: str
):
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


def test_meta(mk_cli_anon: Misskey):
    res = mk_cli_anon.meta()
    assert type(res) == dict


def test_stats(mk_cli_anon: Misskey):
    res = mk_cli_anon.stats()
    assert type(res) == dict


def test_i_favorites(mk_cli_admin: Misskey):
    res = mk_cli_admin.i_favorites()
    assert type(res) == list


def test_should_be_viewable_note(
    mk_cli_admin: Misskey,
    mk_admin_new_note: str
):
    res = mk_cli_admin.notes_show(mk_admin_new_note)
    assert type(res) == dict


def test_note_poll_expires_at(
    mk_cli_admin: Misskey
):
    res = mk_cli_admin.notes_create(
        text='poll test (expires_at)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expires_at=(
            datetime.datetime.now() +
            datetime.timedelta(minutes=1)
        ),
    )
    assert type(res) == dict
    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])

    assert type(is_deleted) == bool
    assert is_deleted


def test_note_poll_expired_after(
    mk_cli_admin: Misskey
):
    res = mk_cli_admin.notes_create(
        text='poll test (expired_after)',
        poll_choices=[
            'test 1',
            'test 2',
        ],
        poll_expired_after=datetime.timedelta(minutes=1),
    )
    assert type(res) == dict
    is_deleted = mk_cli_admin.notes_delete(res['createdNote']['id'])

    assert type(is_deleted) == bool
    assert is_deleted


def test_should_be_error_in_create_note_visibility(
    mk_cli_admin: Misskey,
):
    with pytest.raises(ValueError):
        mk_cli_admin.notes_create(visibility='not valid visibility')


def test_i_notifications(
    mk_cli_admin: Misskey
):
    res = mk_cli_admin.i_notifications(
        include_types=[
            NotificationsType.REACTION
        ],
    )
    assert type(res) == list


def test_should_be_error_in_i_notifications(
    mk_cli_admin: Misskey
):
    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            include_types=[
                'unknown_type'
            ]
        )

    with pytest.raises(ValueError):
        mk_cli_admin.i_notifications(
            exclude_types=[
                'unknown_type'
            ]
        )
