from utils.post_utils import *
from models.user_picked import UserPicked


def scheduled_task(users):
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
            if "中奖" in i or "抽签" in i:
                UserPicked.update(got_prize=True).where(id == user.id)
