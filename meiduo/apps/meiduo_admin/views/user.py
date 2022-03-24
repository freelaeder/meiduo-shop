from rest_framework.generics import ListAPIView

# 用户管理 查询 users/?page=1&pagesize=10&keyword=
from apps.meiduo_admin.serializers.user import UserSerializer
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User


class UserListView(ListAPIView):
    # 指定序列化器
    serializer_class = UserSerializer
    # 分页
    pagination_class = PageNum

    # queryset = User.objects.all()

    # 重写 queryset
    # 意为 指定要查找的哪一张表
    def get_queryset(self):
        # 获取前段传递的值
        keyword = self.request.query_params.get('keyword')
        # print(self.request.query_params.get('page'))
        print(f'keyword{keyword}')
        # 如果为空返回所有数据。反之根据关键字查找
        if keyword is '' or keyword is None:
            return User.objects.all()
        else:
            return User.objects.filter(username=keyword)
