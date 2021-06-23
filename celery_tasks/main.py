from celery import Celery

import os

# 为celery使用django配置文件进行设置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo.settings")

# 创建celery实例
celery_app = Celery('celery_tasks')
# 设置队列为redis，加载config配置文件
celery_app.config_from_object('celery_tasks.config')
# 自动注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms'])
