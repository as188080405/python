from django import http

# Create your views here.
from django.views import View
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection
from utils.constants import IMAGE_CODE_EXPIRE_TIME

class ImageCodeView(View):
    """ 响应图片验证码 """
    def get(self, request, uuid):
        # 使用插件生成图片验证码，返回两个参数（文本和图片）
        text, image = captcha.generate_captcha()
        # 获取redis连接
        redis_conn = get_redis_connection('code')
        # 以图片验证码文本为value，用户UUID信息为key存入reids，待后续和用户输入做验证
        redis_conn.setex('img_%s' %uuid, IMAGE_CODE_EXPIRE_TIME, text)
        # 响应前端图片，告知浏览器使用图片的方式解析
        return http.HttpResponse(image, content_type='image/jpeg')

