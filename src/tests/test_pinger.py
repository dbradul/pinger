import random
import string
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
    def update_db(mode):
        # contacts = Contact.filter(Contact.active == True).order_by(Contact.last_access.desc()).objects()
        contacts = Contact.filter(Contact.active == True).objects()
        if mode == 'all':
            # contact = Contact.select().order_by(fn.Random()).limit(1)
            # print('CONTACTS: %d' % len(contacts))
            for contact in contacts:
                contact.id = ''.join(random.choices(
                    string.ascii_lowercase +
                    string.ascii_uppercase +
                    string.digits,
                    k=10))
                contact.save()
                print(f'Updated contact: {mode} -> {contact}')
        elif mode == 'one':
            contact = Contact.select().order_by(fn.Random()).limit(1)
            contact = contact.get()
            contact.count_requests += 1
            contact.save()
            print(f'Updated contact: {mode} -> {contact}')
        return True

    with ThreadPoolExecutor(max_workers=4) as executor:
            res = executor.map(
                update_db,
                # ('one', 'one', 'one', 'one', 'one', 'one', 'one', 'one', 'all', 'one', 'one', 'one', 'one', 'one', 'one', 'one', 'one')
                # ('all', 'one', 'one', 'one', 'one', 'one', 'one', 'one', 'one')
                ('all', 'one', 'one', 'one', 'one')
                # ('all', 'all')
            )

    assert all(res)
