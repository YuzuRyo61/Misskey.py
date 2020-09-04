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


@pytest.mark.vcr()
def test_reactions(note, api):
    reactions = api.notes_reactions(note["createdNote"]["id"])
    assert isinstance(reactions, list)


@pytest.mark.vcr()
def test_notes(api_anonymous):
    notes = api_anonymous.notes()
    assert isinstance(notes, list)


@pytest.mark.vcr()
def test_notes_renote(note, api2):
    renoted_note = api2.notes_renote(note["createdNote"]["id"])
    assert isinstance(renoted_note, dict)


@pytest.mark.vcr()
def test_notes_renotes(note, api2):
    renotes = api2.notes_renotes(note["createdNote"]["id"])
    assert isinstance(renotes, list)


@pytest.mark.vcr()
def test_notes_polls_vote(api, note_polls):
    res = api.notes_polls_vote(note_polls["createdNote"]["id"], 0)
    assert isinstance(res, bool)
    assert res is True
