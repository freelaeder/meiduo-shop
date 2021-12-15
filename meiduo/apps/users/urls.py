from django.urls import path
# 导入apps下的users中的模型类
from apps.users.views import *

urlpatterns = [
    #  /usernames/ffdsf12/count/ 验证用户名
    path('usernames/<username>/count/', UsernameCountView.as_view())
]
