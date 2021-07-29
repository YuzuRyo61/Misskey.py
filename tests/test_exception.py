import uuid

import pytest

from misskey.exceptions import MisskeyAPIException


def test_should_be_unknown_api_exception():
    mk_ae = MisskeyAPIException({})

    assert mk_ae.code == 'UNKNOWN'
    assert mk_ae.message == 'Unknown exception in Misskey.py'
    assert type(mk_ae.id) == uuid.UUID and mk_ae.id == uuid.UUID(int=0)


@pytest.mark.parametrize('res_dict', [
    {
        'error': {
            'code': 'I_AM_AI',
            'message': 'You sent a request to Ai-chan, Misskey\'s showgirl, instead of the server.',
            'id': '60c46cd1-f23a-46b1-bebe-5d2b73951a84',
        }
    },
    {
        'error': {
            'code': 'TEST',
            'message': 'This message is test for Misskey.py',
            'id': 'this is invalid uuid test'
        }
    }
])
def test_api_exception(res_dict: dict):
    mk_ae = MisskeyAPIException(res_dict)
    assert type(mk_ae.code) == str
    assert type(mk_ae.id) == str or type(mk_ae.id) == uuid.UUID
    assert type(mk_ae.message) == str
    assert type(str(mk_ae)) == str
