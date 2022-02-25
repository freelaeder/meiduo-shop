from django.urls import path
from apps.carts.views import *

urlpatterns = [
    # 购物车 增删改查
    path('carts/', CartsView.as_view()),

]
