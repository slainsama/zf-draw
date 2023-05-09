from flask import Flask, render_template
from flask_apscheduler import APScheduler

from globals.config import manager_token
from utils.schedule_utils import scheduled_task
from utils.user_utils import *

app = Flask(__name__)

URL_TOKEN = manager_token


def add_token(url):
    return '/' + URL_TOKEN + url


@app.route('/')
def index_handler():
    return render_template("index.html")


@app.route(add_token('/status'))
def get_status_handler():
    users = UserPicked.select()
    return render_template("status.html", rows=users)


@app.route(add_token('/adduser/<int:mobile>/<string:password>'))
def add_user_handler(mobile, password):
    message = add_user(mobile, password)
    users = UserPicked.select()
    return render_template("status.html", rows=users, message=message)


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
