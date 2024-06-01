from datetime import datetime

from peewee import *

db = SqliteDatabase('./data/contacts.db')


class BaseModel(Model):
    class Meta:
        database = db


class Contact(BaseModel):
    id = CharField(index=True, unique=True)
    name = CharField()
    active = BooleanField()
    admin = BooleanField(default=False)
    last_access = DateTimeField()
    count_requests = IntegerField(default=0)

    def formatted_info(self):
        return f"{self.name}, {self.last_access}, {self.count_requests}"

    def __str__(self):
        return f"{self.id}, {self.name}, {self.active}, {self.count_requests}"

    def save(self, *args, **kwargs):
        self.last_access = datetime.utcnow()
        super().save(*args, **kwargs)


class History(BaseModel):
    event_date = DateTimeField()
    event_type = CharField()

    def __str__(self):
        return f"{self.event_date}: {self.event_type}"
