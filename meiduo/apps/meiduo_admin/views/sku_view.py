from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKU, SPU, SPUSpecification
from apps.meiduo_admin.serializers.sku_seri import SKUSerializer, SKUCategorieSerializer, GoodsSimpleSerializer, \
    GoodsSpecSerialzier
from apps.meiduo_admin.utils import PageNum
from rest_framework.generics import ListAPIView
from apps.goods.models import GoodsCategory


# sku管理
class SKUModelViewSet(ModelViewSet):
    queryset = SKU.objects.all()
    serializer_class = SKUSerializer
    pagination_class = PageNum


# 获取三级分类信息
class SKUCategoriesView(ListAPIView):
    serializer_class = SKUCategorieSerializer
    # 根据数据存储规律parent_id大于37为三级分类信息，查询条件为parent_id__gt=37
    # queryset = GoodsCategory.objects.filter(parent_id__gt=37)
    # 或者
    queryset = GoodsCategory.objects.filter(subs=None)


# 获取SPU表名称数据
class GoodsSimpleView(ListAPIView):
    serializer_class = GoodsSimpleSerializer
    queryset = SPU.objects.all()


# 获取SPU商品规格信息
class GoodsSpecView(ListAPIView):

    def get_queryset(self):
        pk = self.kwargs['pk']
        return SPUSpecification.objects.filter(spu_id=pk)

    serializer_class = GoodsSpecSerialzier
