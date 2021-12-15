import re

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
        # 再次验证用户的长度
        if not re.match('[a-zA-Z0-9_-]{5,20}', username):
            return JsonResponse({'code': 200, 'errmsg': '用户名不满足需求'})
        count = User.objects.filter(username=username).count()
        return JsonResponse({'code': 0, 'count': count, 'errmeg': 'OK'})


class Usermobiles(View):
    def get(self, request, mobile):
        print(mobile)
        return JsonResponse({'code': 0, 'count': mobile, 'errmeg': 'OK'})
