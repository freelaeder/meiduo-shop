from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.goods.models import GoodsChannel


class IndexView(View):
    def get(self, request):
        # 查询所有的频道，先按照group_id.相等的话，按照sequence
        chanles = GoodsChannel.objects.order_by('group_id', 'sequence')
        # 创建一个空的字典
        categories = {}
        for c in chanles:
            print(c)
            # 当前的组
            if c.group_id not in categories:
                categories[c.group_id] = {'channels': [], 'sub_cats': []}
            category = c.category
            categories[c.group_id]['channels'].append({
                'id': category.id,
                'name': category.name,
                'url': c.url,
            })
            # 组装 2 级 和 3级 分类的数据
            category2 = category.subs.all()  # 获取所有的 2 级分类
            for c2 in category2:
                category3 = c2.subs.all()  # 获取所有的 3 级分类
                sub_cats3 = []  # 存放3级分类的数据
                for c3 in category3:
                    sub_cats3.append({
                        'id': c3.id,
                        'name': c3.name
                    })
                categories[c.group_id]['sub_cats'].append({
                    'id': c2.id,
                    'name': c2.name,
                    'sub_cats': sub_cats3
                })

        print(categories)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
