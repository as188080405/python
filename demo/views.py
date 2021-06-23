import logging

from django.http import HttpResponse

# Create your views here.
from django.shortcuts import render

def test_jinja2(request):
    print('开始处理【test_jinja2】请求')
    logger = logging.getLogger('django')
    logger.info('测试info')
    logger.debug('测试debug')
    logger.error('测试error')

    context = {
        'name': '杨幂',
        'age': 18,
    }
    return render(request, 'test.html', context)
