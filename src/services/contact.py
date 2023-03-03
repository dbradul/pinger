from peewee import fn, ModelSelect

from common.models import Contact


class ContactService:
    @staticmethod
    def subscribe(contact: Contact) -> None:
        contact.active = True
        contact.save()

    @staticmethod
    def unsubscribe(contact: Contact) -> None:
        contact.active = False
        contact.save()

    @staticmethod
    def increase_requests_counter(contact: Contact) -> None:
        contact.count_requests += 1
        contact.save()

    @staticmethod
    def touch(contact: Contact) -> None:
        contact.save()

    @staticmethod
    def get_recently_active_contacts(limit: int = 10) -> ModelSelect:
        return (Contact
                .filter()
                .order_by(Contact.last_access.desc())
                .limit(limit)
                .objects()
        )

    @staticmethod
    def get_subscribers(random_sort: bool = False) -> ModelSelect:
        # look_back_window = datetime.utcnow() - timedelta(minutes=0)
        contacts = Contact.filter(
            Contact.active == True,
            # Contact.last_access <= look_back_window
        )
        if random_sort:
            contacts = contacts.order_by(fn.Random())
        return contacts.objects()

    def get_engaged_contacts(self) -> ModelSelect:
        return self.get_by_filter(
            (Contact.active == True) |
            (Contact.count_requests > 0)
        )

    @staticmethod
    def get_by_filter(filter) -> ModelSelect:
        return Contact.select().where(filter).objects()

    @staticmethod
    def get_all() -> ModelSelect:
        return Contact.filter().objects()

    @staticmethod
    def get_greeting(contact: Contact) -> str:
        invitation = (
            'Вітаю' if contact.name == 'Subscriber'
            else f'Вітаю, {contact.name}'
        )
        return invitation
