from peewee import *

db = SqliteDatabase('./data/contacts.db')

class Contact(Model):
    id = CharField()
    name = CharField()
    active = BooleanField()
    last_access = DateTimeField()

    class Meta:
        database = db

    def info(self):
        return f"{self.name}, {self.last_access}"

    def __str__(self):
        return f"{self.id}, {self.name}, {self.active}, {self.last_access}"