import pytest

from misskey.base import BaseMisskey


def test_base_init_should_be_https_default():
    """
    If only a domain is entered, the https protocol must be given.
    """
    mk = BaseMisskey(
        address="misskey.example.com",
    )
    assert mk.address == "https://misskey.example.com"


def test_base_init_should_be_http():
    """
    If an address is entered with the http protocol, it should remain http
    """
    mk = BaseMisskey(
        address="http://misskey.example.com",
    )
    assert mk.address == "http://misskey.example.com"


def test_base_init_slash_should_strip():
    """
    The trailing slash in the address must be removed.
    """
    mk = BaseMisskey(
        address="https://misskey.example.com/",
    )
    assert mk.address == "https://misskey.example.com"


def test_base_init_raise_not_supported_protocol():
    """
    That a ValueError is sent if a protocol other than
    http or https is entered.
    """
    with pytest.raises(ValueError):
        BaseMisskey(
            address="ssh://misskey.example.com/",
        )


def test_base_init_token_is_same():
    """
    The assigned 'token' must be the same.
    """
    mk = BaseMisskey(
        address="https://misskey.example.com",
        token="abcdef1234567890",
    )
    assert mk.token == "abcdef1234567890"
