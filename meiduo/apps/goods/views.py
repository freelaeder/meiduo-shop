from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.ad.models import ContentCategory
from apps.goods.models import GoodsChannel
from utils.goods_utils import get_categories


class IndexView(View):
    def get(self, request):
        try:
            categories = get_categories()
        except Exception as e:
            print(e)
            return {'code': 1, 'errmsg': 'get data error'}

        # huo qu guanggao shuju
        contents = {}

        # - 1 ContentCategory获取所有广告的类别
        content_categories = ContentCategory.objects.all()
        # - 2 遍历所有的类别 获取每个类别下的广告
        for content_cat in content_categories:
            content_items = content_cat.content_set.filter(status=True).order_by('sequence')
            #   - 获取的时候 按照status 过滤
            #   - 按照sequence排序
            content_items_list = []
            for item_c in content_items:
                content_items_list.append(item_c.to_dict())

            contents[content_cat.key] = content_items_list

        print(contents)

        return JsonResponse({'code': 0, 'errmsg': 'ok', "categories": categories, 'contents': contents})
        # return render(request, 'index.html', context)
