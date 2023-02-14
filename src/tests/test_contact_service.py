from concurrent.futures import ThreadPoolExecutor

import pytest
from peewee import fn

from common.models import Contact
from services import ContactService


@pytest.fixture()
def contact_service(app) -> ContactService:
    return app.container.contact_service()





@pytest.fixture(autouse=True)
def populate_db(test_db):
    Contact.insert_many([
        {'id': 1, 'last_access': '2023-01-01', 'name': 'Test User1', 'active': 1, 'count_requests': 0},
        {'id': 2, 'last_access': '2023-01-01', 'name': 'Test User2', 'active': 1, 'count_requests': 1},
        {'id': 3, 'last_access': '2023-01-01', 'name': 'Test User3', 'active': 0, 'count_requests': 0},
        {'id': 4, 'last_access': '2023-01-01', 'name': 'Test User4', 'active': 0, 'count_requests': 1},
    ]).execute()

# def test_pinger(client, app):
#     # mocker.patch(
#     #     'main.notify_subscribers',
#     #     return_value=5
#     # )
#     # response = client.get('/init_db')
#     # print(type(client), type(app))
#     # assert response.status_code == 200
#     # print(response)
#
#     assert True


# def test_db_concurrency():
#     contacts = Contact.select().order_by(fn.Random()).limit(10).objects()
#     # if contact:
#     #     contact = contact.get()
#
#     print("CONTACT: ", contacts.count())
#
#
#     def update_db(_):
#         contact = Contact.select().order_by(fn.Random()).limit(1)
#         if contact:
#             contact = contact.get()
#             contact.count_requests += 1
#             contact.save()
#             # print(f'Updated contact: {_} -> {contact}')
#         return True
#
#     with ThreadPoolExecutor(max_workers=32) as executor:
#         res = executor.map(
#             update_db,
#             range(128)
#         )
#
#     assert all(res)
#
#     assert True


def test_subscribers(contact_service: ContactService):
    subscribers = contact_service.get_subscribers(random_sort=True)
    assert 2 == subscribers.count()


def test_engaged_contacts(contact_service: ContactService):
    engaged_contacts = contact_service.get_engaged_contacts()
    assert 3 == engaged_contacts.count()


def test_subscription(contact_service: ContactService, random_user: Contact):
    contact_service.unsubscribe(random_user)
    assert not random_user.active

    contact_service.subscribe(random_user)
    assert random_user.active


def test_touch(contact_service: ContactService, random_user: Contact):
    contact_service.touch(random_user)
    assert contact_service.get_recently_active_contacts(limit=1)[0] == random_user


def test_save(contact_service: ContactService, random_user: Contact):
    random_user.save()
    assert contact_service.get_recently_active_contacts(limit=1)[0] == random_user


