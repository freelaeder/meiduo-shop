from datetime import date, timedelta

from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ordes.models import OrderInfo
from apps.users.models import User


# 获取日活用户的数量
class UserActiveCount(APIView):
    # 指定权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当前日期
        now_date = date.today()
        print(f'now_date{now_date}')
        # 获取日活用户
        try:
            count = User.objects.filter(last_login__gte=now_date).count()
        except Exception as e:
            print(e)
            return Response({'code': 400, 'errmsg': 'err'})
        return Response({
            'count': count,
            'date': now_date
        })


# 日下单用户
class UserOrderCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当天的日期
        now_date = date.today()
        try:
            # 获取日下单的用户数量
            count = OrderInfo.objects.filter(create_time__gte=now_date).count()
            print(count)
        except Exception as e:
            print(e)
            return Response({'code': 400, 'errmsg': 'err'})
        # 返回数量
        return Response({
            'count': count,
            'date': now_date
        })


# 月增用户统计
class UserMonthCount(APIView):
    # 添加权限
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 获取当天的日期
        now_date = date.today()
        # 获取一个月之前的数据
        start_date = now_date - timedelta(days=30)
        print(f'start_date{start_date}')
        # 创建空的列表
        date_list = []

        # 循环添加
        for i in range(30):
            # 循环获取当前的日期
            index_date = start_date + timedelta(days=i)
            # 指定下一天的日期
            cur_date = index_date + timedelta(days=1)
            # 查询条件大于当天日期，小于明天日期
            count = User.objects.filter(date_joined__gte=index_date, date_joined__lt=cur_date).count()

            date_list.append({
                'count': count,
                'date': index_date
            })
        # 返回结果
        return Response(date_list)


# 日增用户统计
class UserDayCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        #  获取当前日期
        now_date = date.today()
        # 获取当天的用户新增数量
        count = User.objects.filter(date_joined__gte=now_date).count()

        # 返回结果
        return Response({
            'count': count,
            'date': now_date
        })


# 用户总数
class UserCount(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 连接数据库返回数量
        try:
            count = User.objects.count()
        except Exception as e:
            print(e)
            return Response({'code': 400, 'errmsg': 'err'})
        return Response({
            'count': count
        })
