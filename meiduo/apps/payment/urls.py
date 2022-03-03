from django.urls import path
from apps.payment.views import *

urlpatterns = [
    # 返回支付链接
    path('payment/<int:order_id>/', PaymentView.as_view()),
    # 保存支付结果
    path('paymemt/status/', PaymentstatusView.as_view()),
]
