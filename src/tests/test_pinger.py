from concurrent.futures import ThreadPoolExecutor

import pytest
from peewee import fn

from src.pinger.models import Contact


def test_pinger(client):
    # mocker.patch(
    #     'main.notify_subscribers',
    #     return_value=5
    # )
    response = client.get('/init_db')
    # assert response.status_code == 200
    print(response)



def test_db_concurrency(client):
    def update_db(_):
        contact = Contact.select().order_by(fn.Random()).limit(1)
        if contact:
            contact = contact.get()
            contact.count_requests += 1
            contact.save()
            print(f'Updated contact: {_} -> {contact}')
        # contact = Contact.get(Contact.id == '123')
        # contact.count_requests += 1
        # contact.save()
        return True

    with ThreadPoolExecutor(max_workers=32) as executor:
            res = executor.map(
                update_db,
                range(128)
            )

    assert all(res)

