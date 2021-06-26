from django.conf.urls import url

from apps.users import views

urlpatterns = [
    # 响应注册页面/用户注册
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    # 验证用户名是否重复ajax
    url(r'^usernames/(?P<username>[a-zA-Z0-9]{5,20})/count/$', views.UsernameCountView.as_view(), name='usernameCount'),
    # 验证手机是否重复ajax
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobileCount'),
    # 发送短信验证码ajax
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view(), name='smsCode'),
    # 响应登录页
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    # 用户退出登录
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
]
