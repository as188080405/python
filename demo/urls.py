from django.conf.urls import url

from demo.views import test_jinja2

urlpatterns = [
    url(r'^test_jinja2/$', test_jinja2),
]