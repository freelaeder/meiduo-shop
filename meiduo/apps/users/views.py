import json
import re
from django import http
import redis
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
        print('前端的数据--', date_dict)
        # {'username': 'freelaeder', 'password': '926400lolo', 'password2': '926400lolo',
        # 'mobile': '18916219220', 'sms_code': '23423', 'allow': True}
        username = date_dict.get('username')
        password = date_dict.get('password')
        password1 = date_dict.get('password2')
        mobile = date_dict.get('mobile')
        sms_code = date_dict.get('sms_code')
        allow = date_dict.get('allow')
        # 验证数据 ------------------
        # 判断参数是否齐全
        if not all([username, password, password1, mobile, allow]):
            return http.JsonResponse({'code': 400, 'errmsg': '缺少必传参数!'})
        # 判断用户名是否是5-20个字符
        if not re.match(r'^[a-zA-Z0-9_]{5,20}$', username):
            return http.JsonResponse({'code': 400, 'errmsg': 'username格式有误!'})
        # 判断密码是否是8-20个数字
        if not re.match(r'^[0-9A-Za-z]{8,20}$', password):
            return http.JsonResponse({'code': 400, 'errmsg': 'password格式有误!'})
        # 判断两次密码是否一致
        if password != password1:
            return http.JsonResponse({'code': 400, 'errmsg': '两次输入不对!'})
        # 判断手机号是否合法
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return http.JsonResponse({'code': 400, 'errmsg': 'mobile格式有误!'})
        # 判断是否勾选用户协议
        if allow != True:
            return http.JsonResponse({'code': 400, 'errmsg': 'allow格式有误!'})

        # 获取redis 中的短信验证码
        try:
            from django_redis import get_redis_connection
            redis_cli = get_redis_connection('code')
            # 1.5 获取redis 数据redis 中存的 短信验证码
            # 通过手机为键 验证码为值 获取
            redis_sms_code: str = redis_cli.get(mobile)
            print('reids---短信验证码', redis_sms_code)
            # 如果找不到返回
            if redis_sms_code is None:
                return JsonResponse({'code': 1, 'errmsg': '用户短信验证错误'})
            redis_sms_code = redis_sms_code.decode()
            print(redis_sms_code, 'redis')
            if sms_code != redis_sms_code:
                return JsonResponse({'code': 1, 'errmsg': '用户输入的短信验证错误'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 1, 'errmsg': '用户短信验证错误11'})
        # ----------------------------------------
        # 保存数据
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except Exception as e:
            return JsonResponse({'coed': 400, 'errmsg': 'err data'})

        # 状态保持
        from django.contrib.auth import login
        login(request, user)
        # 验证短信验证码输入是否正确
        print('用户输入的短信验证码', sms_code)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
