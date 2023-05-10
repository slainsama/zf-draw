import collections
import fileinput

from flask import Flask, render_template
from flask_apscheduler import APScheduler

from globals.config import *
from log.log_init import log_init
from models.user_picked import UserPicked
from spider_models.user import User
from utils.schedule_utils import scheduled_task
from utils.user_utils import load_from_database, add_user, cleanup_all

app = Flask(__name__)

log_init()

URL_TOKEN = manager_token

information = '''use '/<manager_token>/status' to see users' status.
use '/<manager_token>/logs' to see logs.
use '/<manager_token>/msgs/<user_id>' to see the user's msg.
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
    lines = collections.deque(maxlen=500)
    for line in fileinput.input('logs.log'):
        lines.append(line.strip())
    lines.reverse()
    return render_template("logs.html", information=information, logs=lines)


@app.route(add_token('/adduser/<int:mobile>/<string:password>'))
def add_user_handler(mobile, password):
    message = add_user(mobile, password)
    users = UserPicked.select()
    return render_template("status.html", rows=users, message=message, information=information)


@app.route(add_token('/msgs/<int:user_id>'))
def get_msg_handler(user_id):
    for user in User.user_list:
        if int(user.id) == user_id:
            msg_list = user.get_msg()
            return render_template("msgs.html", information=information, nickname=user.nickname, msgs=msg_list)
    return render_template("msgs.html", information=information, nickname=user_id,
                           msgs=["Invalid user id, please check user "
                                 "list!"])


@app.route(add_token('/msgs'))
def get_all_msg_handler():
    msg_list = list()
    for user in User.user_list:
        msg_list.extend(user.get_msg())
    return render_template("msgs.html", information=information, nickname="all user", msgs=msg_list)


if __name__ == '__main__':
    try:
        load_from_database()
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
        app.run(host=host, port=port, debug=debug)
    except Exception as e:
        print(e)
        cleanup_all()
