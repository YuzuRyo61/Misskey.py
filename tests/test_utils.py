import pytest
from Misskey.Util import username_available
from .conftest import make_rc


@pytest.mark.vcr()
def test_username_available(api):
    res_available = username_available("demo.misskey.io", f"MKPU_{make_rc()}")
    assert res_available["available"] is True
    exists_username = api.i()["username"]
    res_unavailable = username_available("demo.misskey.io", exists_username)
    assert res_unavailable["available"] is False
