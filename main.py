from flask import Flask, render_template
from flask_apscheduler import APScheduler

from globals.config import manager_token
from models.user_picked import UserPicked
from utils.schedule_utils import scheduled_task
from utils.user_utils import load_from_database, add_user, cleanup_all
from spider_models.user import User

from log.log_init import log_init


app = Flask(__name__)

log_init()

URL_TOKEN = manager_token

information = '''use '/<manager_token>/status' to see users' status.
use '/<manager_token>/logs' to see logs.
use '/<manager_token>/adduser/<user_mobile>/<user_passowrd>' to add a user.
'''


def add_token(url):
    return '/' + URL_TOKEN + url


@app.route('/')
def index_handler():
    return render_template("index.html", information=information)


@app.route(add_token('/status'))
def get_status_handler():
    users = UserPicked.select()
    return render_template("status.html", rows=users, information=information)


@app.route(add_token('/logs'))
def get_logs_handler():
    with open('logs.log', 'r') as file:
        lines = [line.strip() for line in file.readlines()[:500]]
        file.close()
    return render_template("logs.html", information=information, logs=lines)


@app.route(add_token('/adduser/<int:mobile>/<string:password>'))
def add_user_handler(mobile, password):
    message = add_user(mobile, password)
    users = UserPicked.select()
    return render_template("status.html", rows=users, message=message, information=information)


if __name__ == '__main__':
    try:
        load_from_database()
        print(User.user_list)
        scheduler = APScheduler()
        app.config['SCHEDULER_API_ENABLED'] = True
        app.config['JOBS'] = [
            {
                'id': 'spider',
                'func': scheduled_task,
                'args': [User.user_list],
                'trigger': 'interval',
                'seconds': 1800  # 每半小时触发一次任务
            }
        ]
        scheduler.init_app(app)
        scheduler.start()
        app.run()
    except Exception as e:
        print(e)
        cleanup_all()