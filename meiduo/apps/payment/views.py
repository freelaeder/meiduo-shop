from alipay import AliPay
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.ordes.models import OrderInfo
from meiduo import settings
from utils.views import LoginRequiredJSONMixin


class PaymentView(LoginRequiredJSONMixin, View):

    def get(self, request, order_id):
        # 查询要支付的订单
        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])
        except OrderInfo.DoesNotExist:
            return HttpResponseBadRequest('订单信息错误')

        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 创建支付宝支付对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",
            debug=settings.ALIPAY_DEBUG
        )

        # 生成登录支付宝连接
        order_string = alipay.client_api(
            "alipay.trade.page.pay",
            biz_content={
                "out_trade_no": order_id,  # 订单号
                "total_amount": str(order.total_amount),  # 订单金额 注意传字符串
                "subject": "美多%s" % order.order_id,  # 标题 可以自己写
                "product_code": 'FAST_INSTANT_TRADE_PAY'  # 必传字段
            },
            return_url=settings.ALIPAY_RETURN_URL,  # 回调页面
        )

        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        print('alipay_url', alipay_url)
        return JsonResponse({'code': 0, 'errmsg': 'OK', 'alipay_url': alipay_url})
