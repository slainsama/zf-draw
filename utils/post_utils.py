import logging
import time
import requests
from models.user_picked import *
from spider_models.user import *
import random
import json
from utils.user_utils import get_random_user


def get_list(offset=False):
    random_user=get_random_user()
    random_user.get_list()