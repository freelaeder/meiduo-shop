from rest_framework import serializers

from apps.goods.models import SKUImage, SKU


class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = '__all__'


class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ('id', 'name')

