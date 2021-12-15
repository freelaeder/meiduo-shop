from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# 导入 apps下的users子应用的models 模型类
from apps.users.models import *


# Create your views here.

class UsernameCountView(View):
    def get(self, request, username):
        """
        验证拥护名是否重复
        :param request: 请求对象
        :param username: 用户名
        :return: JSON
        """
        print(username)
        count = User.objects.filter(username=username).count()
        print(count)
        return JsonResponse({'code': 0, 'count': count, 'errmeg': 'OK'})
