import pytest


@pytest.mark.vcr()
def test_meta(api_anonymous):
    meta = api_anonymous.meta()
    assert isinstance(meta, dict)


@pytest.mark.vcr()
def test_stats(api_anonymous):
    stats = api_anonymous.stats()
    assert isinstance(stats, dict)


@pytest.mark.vcr()
def test_pinnedUsers(api_anonymous):
    pinnedUsers = api_anonymous.pinnedUsers()
    assert isinstance(pinnedUsers, list)
