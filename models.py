"""
Models contains the sqlite3 database models for the application.
"""

from peewee import SqliteDatabase
from peewee import Model
from peewee import CharField

database = SqliteDatabase('database.db')


class BaseModel(Model):
    """ Base model for all the database models. """
    class Meta:
        database = database


class User(BaseModel):
    """
    User represent an user for the application.
    """

    first_name = CharField()
    last_name = CharField()
    email = CharField(unique=True)
    password = CharField()

    def get_json(self):
        """
        Returns a dict describing the object, ready to be jsonified.
        """

        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email
        }