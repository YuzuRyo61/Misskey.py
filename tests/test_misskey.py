import pytest

import requests

from misskey import Misskey
from misskey.exceptions import MisskeyAuthorizeFailedException

TEST_HOST = 'http://localhost:3000'


@pytest.mark.parametrize('host', [
    'http://unknown-host',
    'unknown-host',
])
def test_should_connect_error_in_init(host):
    with pytest.raises(requests.exceptions.ConnectionError):
        Misskey(host)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, '')
])
def test_should_token_error_in_init(host, token):
    with pytest.raises(MisskeyAuthorizeFailedException):
        Misskey(host, i=TEST_HOST)


@pytest.mark.parametrize('host, token', [
    (TEST_HOST, 'this_is_invalid'),
    (TEST_HOST, ''),
])
def test_should_token_error_in_setter(host, token):
    with pytest.raises(MisskeyAuthorizeFailedException):
        mk = Misskey(host)
        mk.token = token
