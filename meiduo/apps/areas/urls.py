from django.urls import path
# 导入apps下的users中的模型类
from apps.areas.views import *

urlpatterns = [
    # 获取所有的省
    path('areas/', AreasView.as_view()),
    # 获取省下的市
    path('areas/<area_id>/', SubAreasView.as_view()),
    # 保存地址
    path('addresses/create/', AddresView.as_view()),
    # 展示 地址
    path('addresses/', AddresView.as_view()),
    # addresses/2/default/ 设置默认 put
    path('addresses/<did>/default/', DefaultView.as_view()),
    # 删除 地址 addresses/1/ delete
    # 修改 地址 put addresses/2/
    path('addresses/<did>/', AdrressSetView.as_view()),
    # 修改title addresses/2/title/ put
    path('addresses/<did>/title/', TitleView.as_view()),
    # 修改密码 /password/ put
    path('password/', PasswordView.as_view()),

]
