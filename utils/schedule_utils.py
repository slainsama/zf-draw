import utils.user_utils
from utils.post_utils import *
from models.user_picked import UserPicked
from spider_models.user import User
from typing import List


def autoreply_task(users: List[User]):
    handled_post_list = get_list()
    handled_post_list.sort()
    logging.info(f"handled_posts:{handled_post_list}")
    for user in users:
        for post_id in handled_post_list:
            if user.last_replied < post_id:
                user.reply(post_id)
                time.sleep(random.randint(10, 30))
        msg_list = user.get_msg()
        for i in msg_list:
            if "抽签助手" in i[2]:
                UserPicked.update(got_prize=True).where(id == user.id)


def signin_task(users: List[User]):
    logging.info(f"start signin task")
    for user in users:
        user.sign_in()
        time.sleep(random.randint(10, 30))
