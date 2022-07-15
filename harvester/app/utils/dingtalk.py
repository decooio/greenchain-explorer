# desc  it will send a alert to dingding while harvester adding block failed(compressing alert for 30 minutes)
from dingtalkchatbot.chatbot import DingtalkChatbot
from redis import StrictRedis, ConnectionPool
import time

import os
REDIS_URL = os.environ.get('CELERY_BACKEND')
DINGTALK_ACCESS_TOKEN = os.environ.get('DINGTALK_ACCESS_TOKEN')
DINGTALK_SECRET = os.environ.get('DINGTALK_SECRET')

base_alert = '''
### Harvester添加block失败

### 失败block_hash:

> {0}

### 失败原因:

> {1}
'''
# 区块同步失败告警压缩(1个小时)
alert_delta = 3600

def get_redis_connect():
    pool = ConnectionPool.from_url(REDIS_URL)
    redis_conn = StrictRedis(connection_pool=pool)
    return redis_conn


def get_block_timestamp():
    redis_conn = get_redis_connect()
    result = redis_conn.get('harvester_rsync_error')
    redis_conn.close()
    return result


def set_block_timestamp():
    redis_conn = get_redis_connect()
    redis_conn.set('harvester_rsync_error', int(time.time()))
    redis_conn.close()


def send_dingtalk(block_hash, alert_context):
    '''
    :param block_hash: eg: 0x54b8e9c94026677299afffa72a2d43a450bd17eefa0e64cc2426350f2bf83806
    :param alert_context: str
    :return:
    '''
    if block_hash:
        result = get_block_timestamp()
        if result is None or int(time.time()) - int(result) > alert_delta:
            set_block_timestamp()
            webhook = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(DINGTALK_ACCESS_TOKEN)
            secret = DINGTALK_SECRET
            format_data = base_alert.format(block_hash, alert_context)
            xiaoding = DingtalkChatbot(webhook, secret=secret)
            xiaoding.send_markdown(title='Harvester添加block失败', text=format_data, is_at_all=False)
