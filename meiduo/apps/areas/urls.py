from django.urls import path
# 导入apps下的users中的模型类
from apps.areas.views import *

urlpatterns = [
    # 获取所有的省
    path('areas/', AreasView.as_view()),
    # 获取省下的市
    path('areas/<area_id>/', SubAreasView.as_view())
]
