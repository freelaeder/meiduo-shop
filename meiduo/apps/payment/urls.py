from django.urls import path
from apps.payment.views import *

urlpatterns = [
    # 返回支付链接
    path('payment/<order_id>/', PaymentView.as_view()),
]
