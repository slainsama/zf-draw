from spider_models.user import *


def load_from_database():
    for the_user in UserPicked.select():
        loaded_user = pickle.loads(the_user.data)
        logging.info(f"loaded user {loaded_user.id}-{loaded_user.nickname}")
        User.user_list.append(loaded_user)


def cleanup_all():
    for obj in User.user_list:
        obj.pickle_self()


def add_user(mobile, password):
    try:
        new_user = User()
        new_user.login_with_passwd(mobile, password)
        new_user.pickle_self()
        del new_user
        return "Success added!"
    except Exception as e:
        return e
