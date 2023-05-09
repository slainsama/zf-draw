import logging
import time
import requests
from models.user_picked import *
import random
import json


def get_list(offset=False):
    list_url = 'https://www.zfrontier.com/v2/flow/list'
    headers = {
        'Sec-Ch-Ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'X-Csrf-Token': '1683257553706bcd8ae8ff5087446cbb07fee223',
        'Sec-Ch-Ua-Mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/112.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json, text/plain, */*',
        'X-Client-Locale': 'zh-CN',
        'Sec-Ch-Ua-Platform': '"macOS"',
        'Origin': 'https://www.zfrontier.com',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://www.zfrontier.com/app/circle/1',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'close',
    }
    cookies = {
        'ZF_CLIENT_ID': '1681437772862-6739017236161386',
        '_ga': 'GA1.1.2144246108.1681437773',
        '_bl_uid': 'nqltXgR3fwOwgzmLmxvh1OF5Cps1',
        'Hm_lvt_e76a7af8c582a19dcf7864ab21c83af6': '1681989075,1682084377,1682133885,1683256555',
        'Hm_lpvt_e76a7af8c582a19dcf7864ab21c83af6': '1683257554',
    }
    data = {
        'time': '1683257564',
        't': '18a8a15bebc7ff7785fcfc8bd49e1635',
        'offset': '',
        'cid': '1',
        'sortBy': 'new',
        'tagIds[0]': '2007'
    }
    if offset:
        data['offset'] = offset
    res = requests.post(url=list_url, data=data, headers=headers, cookies=cookies)
    print(res.text)
    list_json = json.loads(res.text)
    offset = list_json['data']['offset']
    post_list = list_json['data']['list']
    print(list_json)
    handled_post_list = list()
    detail_url = 'https://www.zfrontier.com/v2/flow/detail'
    for i in post_list:
        post_hash_id = i['hash_id']
        post_id = i['id']
        data = {'id': post_hash_id}
        res = requests.post(url=detail_url, headers=headers, cookies=cookies, data=data)
        if '待抽奖' in res.text:
            handled_post_list.append(post_id)
    min_last_re = UserPicked.select().get().last_replied
    for user in UserPicked.select():
        if (user.last_replied < min_last_re) and (user.last_replied != 0):
            min_last_re = user.last_replied
    if min_last_re == 0:
        min_last_re = post_list[-1]['id']
    min_post_id = post_list[-1]['id']
    logging.info(f"min_post_id:{min_post_id},min_last_re:{min_last_re}")
    if min_post_id > min_last_re:
        time.sleep(random.randint(3, 10))
        offset_post_list = get_list(offset)
        handled_post_list.extend(offset_post_list)
    return handled_post_list
