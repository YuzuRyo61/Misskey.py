import pytest


@pytest.mark.vcr()
def test_i(api, api2):
    i = api.i()
    i2 = api2.i()
    assert isinstance(i, dict)
    assert isinstance(i2, dict)


@pytest.mark.vcr()
def test_i_update(api, api2):
    __I_UPDATE_NAME = "Misskey.py Unit tester"
    __I2_UPDATE_NAME = "Misskey.py Unit tester 2"
    __I_UPDATE_DESC = "This account is a Misskey.py unit test account. It works automatically."
    i = api.i_update(
        name=__I_UPDATE_NAME,
        description=__I_UPDATE_DESC,
        isBot=True
    )
    i2 = api2.i_update(
        name=__I2_UPDATE_NAME,
        description=__I_UPDATE_DESC,
        isBot=True
    )
    assert i["name"] == __I_UPDATE_NAME
    assert i2["name"] == __I2_UPDATE_NAME
    assert i["description"] == __I_UPDATE_DESC
    assert i2["description"] == __I_UPDATE_DESC
    assert i["isBot"]
    assert i2["isBot"]
