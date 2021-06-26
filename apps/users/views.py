import re
import logging
from random import randint

from django import http
from django.contrib.auth import login, authenticate
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from redis.utils import pipeline

from celery_tasks.sms.tasks import send_sms_code
# from libs.yuntongxun.sms import CCP
from utils import constants

# Create your views here.
from django.urls import reverse
from django.views import View
from apps.users.models import User
from utils.response_code import RETCODE
from django_redis import get_redis_connection

logger = logging.getLogger('django')


# 获取注册页面
class RegisterView(View):

    def get(self, request):
        return render(request, 'register.html')

    # 用户注册
    def post(self, request):
        # 接收参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        mobile = request.POST.get('mobile')
        allow = request.POST.get('allow')
        # 判断参数是否齐全
        if not all([username, password, password2, mobile, allow]):
            return http.HttpResponseBadRequest('缺少必传参数')
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入5-20个字符的用户名')
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.HttpResponseBadRequest('请输入8-20位的密码')
        # 判断两次密码是否一致
        if password != password2:
            return http.HttpResponseBadRequest('两次输入的密码不一致')
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.HttpResponseBadRequest('请输入正确的手机号码')
        # 判断是否勾选用户协议
        if allow != 'on':
            return http.HttpResponseBadRequest('请勾选用户协议')
        # 获取用户输入手机验证码
        sms_code_client = request.POST.get('sms_code')
        # 获取redis中的手机验证码
        redis_conn = get_redis_connection('code')
        sms_code_server = redis_conn.get('sms_%s' % mobile)
        # 判断验证码是否过期
        if sms_code_server is None:
            return render(request, 'register.html', {'sms_code_errmsg': '无效的短信验证码'})
        # 判断验证码是否相同
        if sms_code_client != sms_code_server.decode():
            return render(request, 'register.html', {'sms_code_errmsg': '输入短信验证码有误'})
        try:
           # 保存注册数据
           user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except DatabaseError:
            return render(request, 'register.html', {'register_errmsg': '注册失败！'})
        # 实现状态保持
        login(request, user)
        # 重定向到首页
        response = redirect(reverse('contents:index'))
        # 登录后，用于展示用户名
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


# 验证用户名是否重复
class UsernameCountView(View):
    def get(self, request, username):
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            logger(e)
            return HttpResponse(request, {'code': RETCODE.DBERR, 'count': count})
        return http.JsonResponse({'code': RETCODE.OK, 'count': count})


# 验证手机号是否重复
class MobileCountView(View):
    def get(self, request, mobile):
        try:
            count = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据库异常'})
        return http.JsonResponse({'code': RETCODE.OK, 'count': count})


# 发送短信验证码
class SMSCodeView(View):

    def get(self, request, mobile):
        try:
            # 获取参数
            image_code = request.GET.get('image_code')
            uuid = request.GET.get('uuid')
            # 判断参数是否齐全
            if not ([image_code, uuid]):
                return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '短信验证缺少【image_code, uuid】必传参数'})

            # 获取redis链接
            redis_conn = get_redis_connection('code')
            pl = pipeline('code')
            # 取出图片验证码
            redis_image_code = redis_conn.get('img_%s' % uuid)
            # 删除redis中的图片验证码数据
            redis_conn.delete('img_%s' % uuid)
            # 提取判断是否重复提交短信发送的falg
            send_falg = redis_conn.get('send_falg_%s' % mobile)
            # 当send_falg为1，说明已发送短信，正在短信验证中
            if send_falg:
                return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '发送短信过于频繁'})
        except Exception as e:
            logger.error(e)
            return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'redis数据库异常'})

        # 判断redis中的图片验证码是否存在
        if redis_image_code is None:
            # 不存在返回json响应数据：状态码 / 错误信息
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '短信验证【redis中图片验证码空】'})
        # 比对用户传递的图片验证码和redis中的是否相同
        if redis_image_code.decode().lower() != image_code.lower():  # 转字符串/全部转成小写比较
            # 验证码错误，返回json响应数据：状态码 / 错误信息
            return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '短信验证【图片验证码和redis的不匹配】'})
        # 随机生成短信验证码
        sms_code = '%06d' % randint(0, 999999)
        # 将短信验证码存入redis中，参数【1.key：手机号码，2.短信中提示用户的超时时间：设置为常量，3.发送短信使用的模板：设置为常量】
        # sms_code_key = 'sms_%s' % mobile
        redis_conn.setex('sms_%s' % mobile, constants.SMS_CODE_EXPIRE_TIME, sms_code)
        # 标记falg,区分此手机号码已在发送短信中（避免重复刷新页面，发送短信）
        redis_conn.setex('send_falg_%s' % mobile, constants.SMS_CODE_EXPIRE_TIME, 1)
        # 发送短信:参数(手机号, ['验证码',超时时间], 短信发送模板)
        # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_EXPIRE_TIME], constants.SMS_SEND_TEMPLATE)
        # 异步发送短信
        send_sms_code.delay(mobile, sms_code)
        # 响应结果
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '发送短信成功'})


# 用户登陆
class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 获取请求参数
        username = request.POST.get('username')
        password = request.POST.get('password')
        remembered = request.POST.get('remembered')
        # 判断请求参数
        if not all([username, password]):
            return http.HttpResponseBadRequest('缺少必传参数')
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.HttpResponseBadRequest('请输入正确的用户名或手机号')
        if not re.match(r'^[a-zA-Z0-9]{8,20}$', password):
            return http.HttpResponseBadRequest('密码最少8位，最长20位')
        # 验证用户名密码
        user = authenticate(username=username, password=password)
        # 验证失败响应
        if user is None:
            return render(request, 'login.html', {'account_errmsg': '用户名或密码错误'})
        # 验证成功 - 实现状态保持
        login(request, user)
        # 设置状态保持的周期
        if remembered != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)
        # 登录成功，重定向到首页
        response = redirect(reverse('contents:index'))
        # 登录后，用于展示用户名
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response

