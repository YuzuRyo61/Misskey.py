import pytest
from Misskey.Misskey import Misskey
from Misskey.Exceptions import MisskeyInitException


@pytest.mark.vcr()
def test_constructor():
    Misskey("demo.misskey.io")


@pytest.mark.vcr()
def test_constructor_error():
    with pytest.raises(MisskeyInitException):
        Misskey("example.com")
