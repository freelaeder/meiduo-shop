from django.urls import path
from apps.oauth.views import *

urlpatterns = [
    # 实现QQ登录的路由
    path('qq/authorization/', QQAuthURLView.as_view()),

]
