from django.urls import path
from apps.goods.views import *

urlpatterns = [
    # 展示首页数据
    path('index/', IndexView.as_view()),
    # list/115/skus/?page=1&page_size=5&ordering=-create_time
    path('list/<category_id>/skus/', ListView.as_view()),
    # 热销排行
    path('hot/<category_id>/', HotView.as_view()),
    # 搜索视图
    path('search/', MySearchView()),
    # 商品详情页
    path('detail/<sku_id>/', DetailView.as_view()),
    # 商品访问量
    path('detail/visit/<category_id>/', DetailVisitView.as_view()),
    # 用户浏览记录
    path('browse_histories/', HistoriesView.as_view()),
]
