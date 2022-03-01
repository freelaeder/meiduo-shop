from django.urls import path
from apps.ordes.views import *

urlpatterns = [
    # 结算订单信息展示
    path('orders/settlement/', OrderView.as_view()),
    # 保存订单
    path('orders/commit/', CommitView.as_view()),
]
