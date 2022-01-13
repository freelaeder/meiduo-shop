import json
import re
from django import http
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

# 导入 apps下的users子应用的models 模型类
from apps.users.models import *
# 导入utils
from apps.users.utils import generate_verify_email_url, check_verify_email_token
from celery_tasks.email.tasks import send_email_active
from utils.views import LoginRequiredJSONMixin
from django.contrib.auth import authenticate, login, logout


# Create your views here.
# 验证用户名是否重复


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


# 验证手机号
class Usermobiles(View):
    # 验证手机号
    def get(self, request, mobile):
        try:
            mobile = User.objects.filter(mobile=mobile).count()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 15, 'errmsg': '数据异常'})
        return JsonResponse({'code': 0, 'count': mobile, 'errmeg': 'OK'})


#  完成注册请求
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
            # 如果不等于返回
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
        login(request, user)
        # 验证短信验证码输入是否正确
        print('用户输入的短信验证码', sms_code)

        # 注册时用户名写入到cookie，有效期15天
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


# 用户登录
class loginView(View):

    def post(self, request):
        # 1 接收json数据
        body = request.body
        data_dict = json.loads(body)
        username = data_dict.get('username')
        password = data_dict.get('password')
        remembered = data_dict.get('remembered')
        # 2 验证数据是否为空  正则
        if not all([username, password]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必要参数'})

        import re
        # 验证用户登录方式 手机 账号
        if re.match('^1[3-9]\d{9}$', username):
            # 手机号
            User.USERNAME_FIELD = 'mobile'
        else:
            # account 是用户名
            # 根据用户名从数据库获取 user 对象返回.
            User.USERNAME_FIELD = 'username'

        # 3 验证码用户名和密码是否正确
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({'code': 400, 'errmsg': '用户名密码错误'})
        print(user)
        # 4 状态保持
        login(request, user)

        # 5 判断是否记住登录
        if remembered:
            # 如果记住:  设置为两周有效
            request.session.set_expiry(None)
        else:
            # 如果没有记住: 关闭立刻失效
            request.session.set_expiry(0)
        # 6 返回响应
        # 注册时用户名写入到cookie，有效期15天
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.set_cookie('username', user.username, max_age=3600 * 24 * 15)
        return response


# 用户退出
class logoutView(View):
    def delete(self, request):
        # 清理session
        logout(request)
        # 退出登录，重定向到登录页
        response = JsonResponse({'code': 0, 'errmsg': 'OK'})
        # 退出登录时清除cookie 中的  username
        response.delete_cookie('username')
        return response


# 用户中心
class userInfoView(LoginRequiredJSONMixin, View):
    def get(self, request):
        print(request.user.username, 'request.user.username')
        print(request.user.mobile, 'request.user.moblie')
        print(request.user.email, '用户的邮箱')
        response = JsonResponse({'code': 0, 'errmsg': '个人中心',
                                 'info_data': {
                                     'username': request.user.username,
                                     'mobile': request.user.mobile,
                                     'email': request.user.email,
                                     'email_active': request.user.email_active,
                                 }
                                 })
        return response


# 添加邮箱 验证
class emailView(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 1.获取json数据，转化为字典
        body = request.body
        data_dict = json.loads(body)
        # 2 从字典里拿到邮箱地址
        email = data_dict.get('email')
        print(email, '用户传递的邮箱')
        # 3 校验
        if not email:
            return JsonResponse({'code': 300, 'errmsg': '邮箱错误'})
        # 4 保存到数据库
        try:
            request.user.email = email
            request.user.save()

        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '邮箱保存失败'})

        # 异步发送认证邮件
        verify_url = generate_verify_email_url(request.user)
        message = '<p>尊敬的用户您好！</p><p>感谢您使用美多商城。</p>' \
                  '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
                  '<p><a href="%s">%s</a></p>' % (email, verify_url, verify_url)

        send_email_active.delay(email, message)

        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'OK'})


# 激活邮箱
class EmailVerifiView(View):
    def put(self, request):
        # 接受请求put 数据
        token = request.GET.get('token')
        # 对token 解密 获取 解密数据中的user_id
        user_id = check_verify_email_token(token)
        print(user_id, 'user_id')
        # 如果找不到 ，说明过期
        if not user_id:
            return JsonResponse({'code': 400, 'errmsg': '激活邮件已经过期'})
        # - 6 根据user_id去数据库查询
        try:
            user = User.objects.get(username=user_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 405, 'errmsg': '当前用户不存在'})
            # - 7 把查到user对象的 email_active字段 改为true 不要忘记save
        user.email_active = True
        user.save()
        print('完成激活')
        return JsonResponse({'code': 0, 'errmsg': '激活成功'})
