from django.urls import path
from apps.oauth.views import *

urlpatterns = [
    # 实现返回微博扫码登录的视图
    path('qq/authorization/', WeiboAuthURLView.as_view()),
    # 登录用户验证的视图
    path('oauth_callback/', WeiboAuthUserView.as_view()),

]
