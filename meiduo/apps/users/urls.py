from django.urls import path
# 导入apps下的users中的模型类
from apps.users.views import *

urlpatterns = [
    #  /usernames/ffdsf12/count/ 验证用户名 get
    path('usernames/<username:username>/count/', UsernameCountView.as_view()),
    # /mobiles/(?P<mobile>1[3-9]\d{9})/count/ get 验证手机号
    path('mobiles/<mobile:mobile>/count/', Usermobiles.as_view()),
    # 验证注册 post
    path('register/', RegisterView.as_view()),
    # 用户名登录
    path('login/', loginView.as_view()),
    # 用户退出
    path('logout/', logoutView.as_view()),
    # 用户信息
    path('info/', userInfoView.as_view()),
    # 添加邮箱
    path('emails/', emailView.as_view()),
    # 激活邮箱
    path('emails/verification/', EmailVerifiView.as_view()),

]
