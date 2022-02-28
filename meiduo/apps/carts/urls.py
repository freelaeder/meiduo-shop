from django.urls import path
from apps.carts.views import *

urlpatterns = [
    # 购物车 增删改查
    path('carts/', CartsView.as_view()),
    # 购物车全选
    path('carts/selection/', CartSelectView.as_view()),
    # 简单购物车
    path('carts/simple/', CartSimpleView.as_view()),

]
