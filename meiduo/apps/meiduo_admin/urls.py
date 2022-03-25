from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token

from apps.meiduo_admin.login import admin_jwt_token
from apps.meiduo_admin.views.image import SKUImageView, SkuImage
from apps.meiduo_admin.views.statistical import UserActiveCount, UserOrderCount, UserMonthCount, UserDayCount, UserCount
from apps.meiduo_admin.views.user import UserListView

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
    # 用户管理 查询 users/?page=1&pagesize=10&keyword=
    path('users/', UserListView.as_view()),
    # skus/simple/ 返回新增商品时的商品id
    path('skus/simple/', SkuImage.as_view()),

]

# 注册视图集
router = DefaultRouter()
# 注册路由
# 获取图片
router.register(prefix='skus/images', viewset=SKUImageView, basename='image')
# 把路由添加到urlpatterns
urlpatterns += router.urls
