from django.http import HttpResponse, JsonResponse
from django.views import View
from django.shortcuts import render

# Create your views here.
from ronglian_sms_sdk import SmsSDK


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
        redis_cli.setex(uuid, 300, text)
        # 4 .返回图片二进制
        # 因为是二级制，不能直接使用JsonResponse返回数据
        # content_type =响应体数据类型
        # 语法形式 大类/小类
        return HttpResponse(image, content_type='image/jpeg')


class SmsCodeView(View):
    """
    验证图形验证码ok，发送短信验证码
    """

    # 1 请求的地址
    # this.host + '/sms_codes/' + this.mobile + '/' +
    # '?image_code=' + this.image_code +
    # '&image_code_id=' + this.image_code_id
    # 2. 获取参数
    def get(self, request, mobile):
        # 1 获取参数
        # image_code 就是用户输入的图形验证码
        image_code: str = request.GET.get('image_code')
        # 前段返回的uuid
        uuid = request.GET.get('image_code_id')
        # 1.2 验证参数是否传递完整 ，否则返回
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': '参数不够'})
        # 1.3 验证图片验证码
        # 1.4 连接redis
        try:
            from django_redis import get_redis_connection
            redis_cli = get_redis_connection('code')
            # 1.5 获取redis 数据redis 中存的 text
            redis_image_code: str = redis_cli.get(uuid)
            # 假设图形验证码过期 返回
            if redis_image_code is None:
                return JsonResponse({'code': 400, 'errmsg': '图片验证码已过期'})
            # 1.6 对比
            # 类型转化
            redis_image_code = redis_image_code.decode()
            if redis_image_code.lower() != image_code.lower():
                return JsonResponse({'code': 400, 'errmsg': '用户输入的图形验证码错误'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '网络异常'})

        # 2 验证短信验证码
        print('发送手机号', mobile)
        # 12 -20 1 先根据key： flag 手机号。获取值
        flag_send = redis_cli.get('flag_%s' % mobile)
        # 如果值存在，返回错误的响应
        if flag_send:
            return JsonResponse({'code': 1, 'errmsg': '短信已经发送，请稍后再试'})
        # 12-20 如果不在，继续向下执行
        # 2.1 生成随机验证码
        from random import randint
        sms_code = '%06d' % randint(0, 999999)
        print('生成的随机验证码', sms_code)
        # 创建 redis 的管道 ，pipline对象
        pl = redis_cli.pipeline()
        # 保存随机验证码 6位
        pl.setex(mobile, 300, sms_code)
        # 12-20 3 发送完保存key： 手机号 ，有效期  value:1
        pl.setex('flag_s' % mobile, 60, 1)
        # 执行请求
        pl.execute()

        # # 保存随机验证码 6位
        # redis_cli.setex(mobile, 300, sms_code)
        # # 12-20 3 发送完保存key： 手机号 ，有效期  value:1
        # redis_cli.setex('flag_s' % mobile, 60, 1)

        smsSdk = SmsSDK(accId='8aaf07087dc23905017dc74ff83701b7',
                        accToken='68507d25130344b58d116d42ce4b131d',
                        appId='8a216da87dc23fe1017dc750a7aa0192')
        # datas image_code , 5是剩余时间
        smsSdk.sendMessage(tid='1', mobile=mobile, datas=(sms_code, 5))

        # 最终返回
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
