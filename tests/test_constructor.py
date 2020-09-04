import pytest
from Misskey.Misskey import Misskey
from Misskey.Exceptions import MisskeyInitException, MisskeyAPITokenException, MisskeyAiException, MisskeyAPIException


@pytest.mark.vcr()
def test_constructor():
    Misskey("demo.misskey.io")


@pytest.mark.vcr()
def test_constructor_error():
    with pytest.raises(MisskeyInitException):
        Misskey("example.com")


@pytest.mark.vcr()
def test_set_apikey_error():
    with pytest.raises(MisskeyAPITokenException):
        api = Misskey("demo.misskey.io")
        api.apiToken = "invalid"


@pytest.mark.vcr()
def test_get_address(api_anonymous):
    assert isinstance(api_anonymous.address, str)
    assert api_anonymous.address == "demo.misskey.io"


@pytest.mark.vcr()
def test_get_version(api_anonymous):
    assert isinstance(api_anonymous.version, str)


@pytest.mark.vcr()
def test_should_not_access_credentials(api_anonymous):
    with pytest.raises(MisskeyAiException):
        api_anonymous.i()


@pytest.mark.vcr()
def test_delete_apiToken(api):
    _api = api
    del _api.apiToken
    assert _api.apiToken is None


@pytest.mark.vcr()
def test_call(api):
    assert isinstance(api("meta"), dict)
    with pytest.raises(MisskeyAPIException):
        api("not_exists")
