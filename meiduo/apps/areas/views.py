from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from apps.areas.models import *


class AreasView(View):
    def get(self, request):
        # 去数据库查询所有的省份数据
        try:
            areas = Area.objects.filter(parent=None)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '数据库异常'})
        else:
            # 添加省的数据
            province_list = []
            for a in areas:
                province_list.append({'id': a.id, 'name': a.name})
        # 返回
        return JsonResponse({'code': 0, 'province_list': province_list})


# 获取省下的市
class SubAreasView(View):
    def get(self, request, area_id):
        # 获取路径中上一级的id
        # 1. 根据上一级 的id 获取下一个的数据（数据库操作）
        try:
            subareas = Area.objects.filter(parent_id=area_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '数据库链接错误'})

        subs = []
        for a in subareas:
            subs.append({'id': a.id, 'name': a.name})
        return JsonResponse({'code': 0, 'sub_data': {'subs': subs}})
