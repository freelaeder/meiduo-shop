import json
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
        # if not re.match('[a-zA-Z0-9_-]{5,20}', username):
        #     return JsonResponse({'code': 200, 'errmsg': '用户名不满足需求'})
        # 再次优化
        try:
            count = User.objects.filter(username=username).count()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 15, 'errmeg': '数据异常'})

        return JsonResponse({'code': 0, 'count': count, 'errmeg': 'OK'})


class Usermobiles(View):
    # 验证手机号
    def get(self, request, mobile):
        try:
            mobile = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 15, 'errmsg': '数据异常'})
        return JsonResponse({'code': 0, 'count': mobile, 'errmeg': 'OK'})


class RegisterView(View):
    """
    完成注册请求
    """

    def post(self, request):
        # 1,接受数据 传递的JSON数据
        body_byte = request.body
        # 把Byte转换成json字典
        date_dict = json.loads(body_byte)
        print(date_dict)
        # {'username': 'freelaeder', 'password': '926400lolo', 'password2': '926400lolo',
        # 'mobile': '18916219220', 'sms_code': '23423', 'allow': True}
        username = date_dict.get('username')
        password = date_dict.get('password')
        password1 = date_dict.get('password2')
        mobile = date_dict.get('mobile')
        sms_code = date_dict.get('sms_code')
        allow = date_dict.get('allow')
        # 验证数据
        # all里面传递
        if not all([username, password1, password, mobile, sms_code, allow]):
            return JsonResponse({'code': 400, 'errmsg': 'err data'})
        try:
            User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            return JsonResponse({'coed': 400, 'errmsg': 'err data'})
        # 状态保持
        from django.contrib.auth import login
        login(request, username)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
