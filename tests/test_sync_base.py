import requests

from misskey.sync_base import Misskey


def test_sync_base_init_session_is_created():
    """
    Automatic creation if the argument session is not set during instantiation.
    """
    mk = Misskey(
        address="https://misskey.example.com",
    )
    assert isinstance(mk.session, requests.Session)


def test_sync_base_init_session_is_same_if_assigned():
    """
    When the argument session is assigned,
    it must match with the corresponding property.
    """
    session = requests.Session()
    mk = Misskey(
        address="https://misskey.example.com",
        session=session,
    )
    assert mk.session == session
