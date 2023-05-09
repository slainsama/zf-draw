from utils.post_utils import *


def scheduled_task(users):
    handled_post_list = get_list()
    handled_post_list.sort()
    print(handled_post_list)
    for user in users:
        for post_id in handled_post_list:
            if user.last_replied < post_id:
                print(post_id)
                print('last_re:', user.last_replied)
                user.reply(post_id)
                time.sleep(random.randint(10, 30))