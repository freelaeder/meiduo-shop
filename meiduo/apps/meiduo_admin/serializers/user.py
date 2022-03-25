from rest_framework import serializers
from apps.users.models import User


# 定已返回的序列化器
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        # 指定表
        model = User
        # 指定字段
        fields = ['id', 'username', 'mobile', 'email', 'password']
        # username 增加1长度限制，passwordz增加只写
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            }
        }
        # 重写create 方法

    def create(self, validated_data):
        # 保存用户数据
        print(f'validated_data{validated_data}')
        user = User.objects.create_user(**validated_data)
        return user
