from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.ad.models import ContentCategory
from apps.goods.models import GoodsChannel, GoodsCategory, SKU
from utils.goods_utils import get_categories, get_breadcrumb


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


# list/115/skus/?page=1&page_size=5&ordering=-create_time
class ListView(View):
    def get(self, request, category_id):
        # 1 接受参数
        page = request.GET.get('page')
        page_size = request.GET.get('page_size')
        ordering = request.GET.get('ordering')
        print(category_id)
        # 2 获取商品分类的数据
        try:
            category = GoodsCategory.objects.get(id=category_id)

        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '商品数据不存在'})
        skus = SKU.objects.filter(category=category, is_launched=True).order_by(ordering)
        # 2 分页
        paginator = Paginator(skus, page_size)
        page_skus = paginator.page(page)
        count = paginator.num_pages
        # - 2.2面包屑导航
        breadcrumb = get_breadcrumb(category)
        # - 热销商品数据 # - 3把数据转为字典 # - 4返回
        sku_list = []
        for sku in page_skus:
            sku_list.append(
                {'id': sku.id,
                 'name': sku.name,
                 'price': sku.price,
                 'default_image_url': sku.default_image.url, })
        return JsonResponse({'code': 0, 'errmsg': "ok", 'count': count, "list": sku_list, 'breadcrumb': breadcrumb})
