from peewee import *
from globals.config import *

DB = MySQLDatabase(db_name, user=db_user, password=db_pass, host=db_host, port=db_port)
