import configparser

config = configparser.ConfigParser()
config.read('./config.ini')

db_host = config.get('database', 'host')
db_port = config.getint('database', 'port')
db_name = config.get('database', 'name')
db_user = config.get('database', 'user')
db_pass = config.get('database', 'password')
db_load=config.getboolean('database','load_from_database')
db_clear=config.getboolean('database','clear_bytes')

manager_token = config.get('token', 'manager_token')

host=config.get('server','host')
port=config.get('server','port')
debug=config.getboolean('server','debug')

signin_interval=config.getint('task','signin_interval')
autoreply_interval = config.getint('task', 'autoreply_interval')