from django.db import transaction
from rest_framework import serializers

from apps.goods.models import SKU, SPU, SpecificationOption, SPUSpecification, SKUSpecification
from apps.goods.models import GoodsCategory


class SKUSpecificationSerialzier(serializers.ModelSerializer):
    """
        SKU规格表序列化器
    """
    spec_id = serializers.IntegerField()
    option_id = serializers.IntegerField()

    class Meta:
        model = SKUSpecification  # SKUSpecification中sku外键关联了SKU表
        fields = ("spec_id", 'option_id')


# sku管理
class SKUSerializer(serializers.ModelSerializer):
    spu_id = serializers.IntegerField()
    category_id = serializers.IntegerField()

    spu = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)

    specs = SKUSpecificationSerialzier(many=True)

    class Meta:
        model = SKU
        fields = '__all__'

    def create(self, validated_data):
        # 获取规格信息,并从validated_data数据中,删除规格信息数据
        specs_data = validated_data.pop('specs')

        with transaction.atomic():
            # 开启事务
            savepoint = transaction.savepoint()
            # 保存sku
            sku = SKU.objects.create(**validated_data)
            # 对规格信息进行遍历,来保存商品规格信息
            for spec_data in specs_data:
                SKUSpecification.objects.create(sku=sku, **spec_data)
            # 清除保存点
            transaction.savepoint_commit(savepoint)
            # 返回sku
            return sku

    def update(self, instance, validated_data):
        # 获取数据删除specs
        specs = validated_data.pop('specs')
        # 调用父类方法
        super().update(instance, validated_data)
        # 循环更新specs
        for spec in specs:
            # 获取最新的规格id
            new_spec_id = spec.get('spec_id')
            # 获取新数据的选项值
            new_option_id = spec.get('option_id')
            SKUSpecification.objects.filter(sku=instance, spec_id=new_spec_id).update(option_id=new_option_id)
        return instance


# 获取三级分类信息
class SKUCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoodsCategory
        fields = "__all__"


# 获取spu表名数据
class GoodsSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = SPU
        fields = '__all__'


# 获取SPU商品规格信息
class GoodOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationOption
        fields = ('id', 'value')


class GoodsSpecSerialzier(serializers.ModelSerializer):
    spu = serializers.StringRelatedField()
    spu_id = serializers.IntegerField()
    # 关联序列化返回 规格选项信息
    options = GoodOptionSerializer(many=True)  # 使用规格选项序列化器

    class Meta:
        model = SPUSpecification  # SPUSpecification中的外键spu关联了SPU商品表
        fields = "__all__"
