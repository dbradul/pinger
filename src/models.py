from peewee import *

db = SqliteDatabase('./data/contacts.db')

class Contact(Model):
    id = CharField()
    name = CharField()
    active = BooleanField()
    last_access = DateTimeField()

    class Meta:
        database = db
