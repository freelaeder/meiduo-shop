"""meiduo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include

# 注意是测试log
# def logs(request):
#     # 1 导入
#     import logging
#     # 2创建日志器
#     logger = logging.getLogger('django')
#     # 3 调动日志器的方法存储日志
#     logger.info('用户登录了')
#     logger.warning('redis缓存不足')
#     logger.error('该记录不存在')
#     logger.debug('我不会被保存，哈喽')
#     return HttpResponse('ok')


# 导入自己定义的转化器
from utils.converters import UsernameConverter, MobileConverter, UUIDConverter
from django.urls import register_converter

# 注册转换器 前者是自己定义的转化器，后者是别名
register_converter(UsernameConverter, 'username')
# 验证手机号
register_converter(MobileConverter, 'mobile')
# 验证uuid
register_converter(UUIDConverter, 'uuid')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('log/', logs)
    # 添加子应用的urls
    path('', include('apps.users.urls')),
    # 验证图片验证码 短信验证码
    path('', include('apps.verifications.urls')),
    # 实现weibo扫码登录
    path('', include('apps.oauth.urls')),
    # 地区
    path('', include('apps.areas.urls')),
    # 首页 展示
    path('', include('apps.goods.urls')),
]
