from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.login import admin_jwt_token
from apps.meiduo_admin.views.statistical import UserActiveCount, UserOrderCount, UserMonthCount, UserDayCount, UserCount

urlpatterns = [
    # path('authorizations/', obtain_jwt_token)
    # 验证用户是否为管理员
    path('authorizations/', admin_jwt_token),
    # statistical/day_active/ 日活用户
    path('statistical/day_active/', UserActiveCount.as_view()),
    # 日下单用户量统计
    path('statistical/day_orders/', UserOrderCount.as_view()),
    # 月增用户统计
    path('statistical/month_increment/', UserMonthCount.as_view()),
    # 日增用户统计
    path('statistical/day_increment/', UserDayCount.as_view()),
    # 用户总数
    path('statistical/total_count/', UserCount.as_view()),
]
