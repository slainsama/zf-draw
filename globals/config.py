import configparser

config = configparser.ConfigParser()
config.read('./config.ini')

db_host = config.get('database', 'host')
db_port = config.getint('database', 'port')
db_name = config.get('database', 'name')
db_user = config.get('database', 'user')
db_pass = config.get('database', 'password')

manager_token = config.get('token', 'manager_token')
