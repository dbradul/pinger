import pytest

def test_pinger(mocker):
    mocker.patch(
        'main.notify_subscribers',
        return_value=5
    )
