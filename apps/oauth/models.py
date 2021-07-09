from django.db import models

# Create your models here.
from utils.models import BaseModel


# QQ登录model
class OauthQQUser(BaseModel):

    user = models.ForeignKey('users.User', verbose_name='用户', on_delete=models.CASCADE)
    openid = models.CharField(max_length=64, verbose_name='openid', db_index=True)  # code

    class Meta:
        db_table = 'tb_oauth_qq'
        verbose_name = 'QQ登录用户数据'
        verbose_name_plural = verbose_name
