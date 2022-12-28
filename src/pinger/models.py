from peewee import *

db = SqliteDatabase('./data/contacts.db')

class Contact(Model):
    id = CharField(index=True, unique=True)
    name = CharField()
    active = BooleanField()
    last_access = DateTimeField()
    count_requests = IntegerField(default=0)

    class Meta:
        database = db

    def formatted_info(self):
        return f"{self.name}	{self.last_access}	{self.count_requests}"

    def __str__(self):
        return f"{self.id}, {self.name}, {self.active}, {self.count_requests}"


class History(Model):
    event_date = DateTimeField()
    event_type = CharField()

    class Meta:
        database = db

    def __str__(self):
        return f"{self.event_date}: {self.event_type}"
