import re

from django.contrib.auth.backends import ModelBackend

from apps.users.models import User


# 判断用户是用手机号登录，还是用户名登录
def get_user_by_account(account):
    try:
        if re.match(r'^1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user


# 自定义用户认证
class UsernameMobileAuthBackend(ModelBackend):
    # 重写认证方法
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 根据用户输入的手机号/用户名，查找到用户对象
        user = get_user_by_account(username)
        # 校验user是否存在，并校验密码是否正确
        if user and user.check_password(password):
            return user
