from django.contrib.auth.models import Permission, Group
from rest_framework import serializers
from django.contrib.auth.models import ContentType

# 管理员管理
from apps.users.models import User


# 权限管理
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


# 添加全选管理时，需要的选项
class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ('id', 'name')


# 组的管理
class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        # 调用父类的方法创建用户对象
        user = super().create(validated_data)
        # 从validated_data get password
        password = validated_data.get('password')
        # 重新设置密码
        user.set_password(password)
        # 设置is_staff
        user.is_staff = 1
        # 保存
        user.save()
        # 返回对象
        return user

    def update(self, instance, validated_data):
        # 调用父类更新数据
        super().update(instance, validated_data)
        # 获取密码
        password = validated_data.get('password')
        if password:
            instance.set_password(password)
            instance.save()
        return instance
