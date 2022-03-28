from rest_framework import serializers

from apps.goods.models import SKUImage, SKU

# 返回图片
class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'


# 返回商品新增时的选项
class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name')
