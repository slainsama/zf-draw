from peewee import *
import globals


class UserPicked(Model):
    id = IntegerField(unique=True)
    nickname = CharField()
    mobile = CharField()
    password = CharField(null=False)
    last_replied = IntegerField()
    data = BlobField(null=False)
    status = BooleanField()
    got_prize=BooleanField()

    class Meta:
        database = globals.DB


globals.DB.create_tables([UserPicked])