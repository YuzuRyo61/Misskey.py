import uuid
from urllib.parse import (
    urlparse,
    parse_qs,
)

import pytest
import requests

from misskey import MiAuth
from misskey.enum import Permissions
from misskey.exceptions import MisskeyMiAuthFailedException
from .conftest import TEST_HOST


def test_address_parse():
    ma = MiAuth(
        address='example.com'
    )
    assert type(ma.address) == str
    assert ma.address == 'example.com'


def test_init_no_permission():
    ma = MiAuth(
        address=TEST_HOST,
        permission=[],
    )
    assert type(ma.permission) == list
    assert len(ma.permission) == 0


def test_custom_session_id():
    ma = MiAuth(
        address=TEST_HOST,
        session_id=str(uuid.uuid4())
    )
    assert type(ma.session_id) == str


def test_gen_url_with_optional_params():
    callback_url = 'https://example.com/callback'
    icon_url = 'https://example.com/icon.png'

    ma = MiAuth(
        address=TEST_HOST,
        callback=callback_url,
        icon=icon_url,
    )
    auth_url = ma.generate_url()
    assert type(auth_url) == str

    auth_url_parse = urlparse(auth_url)
    auth_url_parse_query = parse_qs(auth_url_parse.query)
    assert auth_url_parse_query.get('icon') is not None
    assert auth_url_parse_query['icon'][0] == icon_url

    assert auth_url_parse_query.get('callback') is not None
    assert auth_url_parse_query['callback'][0] == callback_url


def test_miauth_invalid_permission():
    with pytest.raises(ValueError):
        MiAuth(
            permission=[
                'invalid_permission'
            ]
        )


def test_miauth_valid_permission():
    MiAuth(
        permission={
            Permissions.READ_ACCOUNT,
        },
    )


def test_attr_name():
    test_name = 'test'
    ma = MiAuth(
        address=TEST_HOST,
        name=test_name,
    )
    assert type(ma.name) == str
    assert ma.name == test_name

    test_name = 'new-test'
    ma.name = test_name

    assert type(ma.name) == str
    assert ma.name == test_name


def test_attr_icon():
    ma = MiAuth(
        address=TEST_HOST,
    )
    assert ma.icon is None

    test_icon_url = 'https://example.com/icon.png'
    ma.icon = test_icon_url

    assert type(ma.icon) == str
    assert ma.icon == test_icon_url

    del ma.icon
    assert ma.icon is None


def test_attr_callback():
    ma = MiAuth(
        address=TEST_HOST,
    )
    assert ma.callback is None

    test_callback_url = 'https://example.com/callback'
    ma.callback = test_callback_url

    assert type(ma.callback) == str
    assert ma.callback == test_callback_url

    del ma.callback
    assert ma.callback is None


def test_permission_setter():
    ma = MiAuth(
        address=TEST_HOST,
    )
    with pytest.raises(ValueError):
        ma.permission = ['invalid_permission']

    ma.permission = (Permissions.READ_ACCOUNT, )
    assert type(ma.permission) == tuple


def test_miauth_check(
    mk_admin_token: str,
):
    ma = MiAuth(
        address=TEST_HOST,
        permission=[],
        name='test-auth'
    )
    with pytest.raises(MisskeyMiAuthFailedException):
        ma.check()

    res = requests.post(
        f'{TEST_HOST}/api/miauth/gen-token',
        json={
            'i': mk_admin_token,
            'name': ma.name,
            'permission': [],
            'session': str(ma.session_id),
        }
    )
    res.raise_for_status()
    res_json = res.json()

    token = ma.check()
    assert token == ma.token == res_json['token']
