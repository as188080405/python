from django.conf.urls import url

from apps.users import views

urlpatterns = [
    url(r'^register/$', views.RegisterView.as_view(), name='register'),  # 响应注册页面/用户注册
    url(r'^usernames/(?P<username>[a-zA-Z0-9]{5,20})/count/$', views.UsernameCountView.as_view(), name='usernameCount'),
    url(r'^mobile/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view(), name='mobileCount'),
    url(r'^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view(), name='smsCode'),
    url(r'^login/$', views.LoginView.as_view(), name='login'),
]
