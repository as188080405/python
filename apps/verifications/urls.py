from django.conf.urls import url

from apps.verifications import views

urlpatterns = [
    url(r'^image_code/(?P<uuid>[\w-]+)/$', views.ImageCodeView.as_view(), name='imageCode')
]