from django.contrib.auth.models import Permission, Group
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet

from apps.meiduo_admin.serializers.permis import AdminSerializer, PermissionSerializer, ContentSerializer, \
    GroupSerializer
from apps.meiduo_admin.utils import PageNum
from apps.users.models import User

from django.contrib.auth.models import ContentType


# 权限管理
class PermissionView(ModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.order_by('id')
    pagination_class = PageNum


# 添加全选管理时，需要的选项
class ContentTypeAPIView(ListAPIView):
    queryset = ContentType.objects.all()
    serializer_class = ContentSerializer

    def get(self, request):
        return self.list(request)


# 组的管理
class GroupView(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = PageNum


# 添加组的时候 获取简单权限列表（辅助组的管理）
class GroupSimpleView(ListAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

    def get(self, request):
        return self.list(request)


# 添加管理员的时候展示组
class AdminSimpleAPIView(ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get(self, request):
        return self.list(request)


# 管理员管理
class PermisAdmins(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = AdminSerializer
    pagination_class = PageNum


