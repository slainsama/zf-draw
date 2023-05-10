from peewee import *
import globals


class UserPicked(Model):
    id = IntegerField(unique=True)
    nickname = CharField()
    mobile = CharField()
    password = CharField()
    last_replied = IntegerField()
    data = BlobField()
    status = BooleanField()
    got_prize=BooleanField()

    class Meta:
        database = globals.DB


globals.DB.create_tables([UserPicked])