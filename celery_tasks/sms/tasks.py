import logging

from celery_tasks.main import celery_app
from libs.yuntongxun.sms import CCP
from utils import constants

logger = logging.getLogger('Django')


# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
@celery_app.task
def send_sms_code(mobile, sms_code):
    # 异步发送短信
    CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRE_TIME], constants.SMS_SEND_TEMPLATE)
    print('短信已发送')

