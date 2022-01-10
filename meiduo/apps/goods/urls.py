from django.urls import path
from apps.goods.views import *

urlpatterns = [
    # 展示首页数据
    path('index/', IndexView.as_view()),

]
