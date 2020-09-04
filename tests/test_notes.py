import pytest


@pytest.mark.vcr()
def test_note(note, api):
    assert isinstance(note, dict)
    note_get = api.notes_show(note["createdNote"]["id"])
    assert isinstance(note_get, dict)
    assert note_get["id"] == note["createdNote"]["id"]


@pytest.mark.vcr()
def test_reaction(note_reaction):
    assert note_reaction is True
