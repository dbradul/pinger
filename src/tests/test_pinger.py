import pytest

def test_pinger(client):
    # mocker.patch(
    #     'main.notify_subscribers',
    #     return_value=5
    # )
    response = client.get('/init_db')
    assert response.status_code == 200
    print(response)