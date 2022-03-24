from rest_framework import serializers

from apps.users.models import User


# 定已返回的序列化器
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定表
        model = User
        # 指定字段
        fields = ['id', 'username', 'mobile', 'email']
