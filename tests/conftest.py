import pytest
import requests

TEST_HOST = 'http://localhost:3000'


@pytest.fixture(scope='session', autouse=True)
def fixture_session():
    res_admin = requests.post(
        f'{TEST_HOST}/api/admin/accounts/create',
        json={
            'username': 'administrator',
            'password': 'administrator_pass',
        }
    )
    res_admin.raise_for_status()

    res_user = requests.post(
        f'{TEST_HOST}/api/signup',
        json={
            'username': 'user',
            'password': 'user_pass',
        }
    )
    res_user.raise_for_status()

    yield res_admin.json()['token'], res_user.json()['token']
