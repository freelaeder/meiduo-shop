from django.http import HttpResponse
from django.views import View
from django.shortcuts import render


# Create your views here.

class ImageCodeView(View):
    def get(self, request, uuid):
        # 1. 接受路由中的uuid
        # 2 生产图片验证码 和二进制
        from libs.captcha.captcha import captcha
        # text是图片验证码的内容
        # image 是图片的二进制
        text, image = captcha.generate_captcha()

        # 3 通过redis 把图片保存起来
        # 3.1 进行redis的链接
        from django_redis import get_redis_connection
        redis_cli = get_redis_connection('code')
        # 3.2 指令操作 name time value
        redis_cli.setex(uuid, 100, text)
        print(uuid)
        # 4 .返回图片二进制
        # 因为是二级制，不能直接使用JsonResponse返回数据
        # content_type =响应体数据类型
        # 语法形式 大类/小类
        return HttpResponse(image, content_type='image/jpeg')
