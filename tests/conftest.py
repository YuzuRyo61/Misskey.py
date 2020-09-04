import random
import string
import pytest
import vcr
import requests

from Misskey.Misskey import Misskey

my_vcr = vcr.VCR(
    serializer='yaml',
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['method', 'query'],
)


def make_rc():
    return "".join(random.choices(string.ascii_letters + string.digits, k=8))


@my_vcr.use_cassette()
def get_test_account_token():
    res = requests.post("https://demo.misskey.io/api/signup",
                        json={
                            "username": f"MPTU_{make_rc()}",
                            "password": make_rc()
                        })
    res.raise_for_status()
    return res.json()["token"]


@my_vcr.use_cassette()
def get_test_account2_token():
    res = requests.post("https://demo.misskey.io/api/signup",
                        json={
                            "username": f"MPTU2_{make_rc()}",
                            "password": make_rc()
                        })
    res.raise_for_status()
    return res.json()["token"]


@pytest.fixture
def api():
    return Misskey("demo.misskey.io", i=get_test_account_token())


@pytest.fixture
def api2():
    return Misskey("demo.misskey.io", i=get_test_account2_token())


@pytest.fixture
def api_anonymous():
    return Misskey("demo.misskey.io")


@pytest.fixture
def note(api):
    _note = api.notes_create("Now testing Note tests")
    yield _note
    api.notes_delete(_note["createdNote"]["id"])


@pytest.fixture
def note2(api2):
    _note = api2.notes_create("Now testing Note tests 2!")
    yield _note
    api2.notes_delete(_note["createdNote"]["id"])


@pytest.fixture
def note_polls(api):
    _note = api.notes_create("This is polls test!",
                             poll=[
                                 "1",
                                 "2"
                             ])
    yield _note
    api.notes_delete(_note["createdNote"]["id"])


@pytest.fixture
def note_reaction(note2, api):
    _reaction = api.notes_reactions_create(note2["createdNote"]["id"], "like")
    yield _reaction
    api.notes_reactions_delete(note2["createdNote"]["id"])


@pytest.fixture(scope="module")
def vcr_config():
    return dict(
        match_on=['method', 'query'],
        decode_compressed_response=True
    )
