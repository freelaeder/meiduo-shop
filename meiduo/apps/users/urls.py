from django.urls import path
# 导入apps下的users中的模型类
from apps.users.views import *

urlpatterns = [
    #  /usernames/ffdsf12/count/ 验证用户名 get
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    # /mobiles/(?P<mobile>1[3-9]\d{9})/count/ get
    path('mobiles/<mobile:mobile>/count/', Usermobiles.as_view()),

]
