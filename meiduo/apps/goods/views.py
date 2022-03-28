import json

from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django_redis import get_redis_connection

# Create your views here.
from django.views import View
from redis import Redis

from apps.ad.models import ContentCategory
from apps.goods.models import GoodsChannel, GoodsCategory, SKU, GoodsVisitCount
from utils.goods_utils import get_categories, get_breadcrumb, get_goods_specs

# 导入:
from haystack.views import SearchView
from django.http import JsonResponse
from utils.views import LoginRequiredJSONMixin


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
                 'default_image_url': sku.default_image.url if sku.default_image else "", })
        return JsonResponse({'code': 0, 'errmsg': "ok", 'count': count, "list": sku_list, 'breadcrumb': breadcrumb})


class HotView(View):
    def get(self, request, category_id):
        skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('sales')[:2]
        # 序列化
        hot_skus = []

        for sku in skus:
            hot_skus.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url if sku.default_image else "",
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'hot_skus': hot_skus})


class MySearchView(SearchView):
    '''重写SearchView类'''

    def create_response(self):
        # 获取搜索结果
        context = self.get_context()
        data_list = []
        for sku in context['page'].object_list:
            data_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url if sku.default_image else "",
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })
        # 拼接参数, 返回
        return JsonResponse(data_list, safe=False)


# 商品详情页
class DetailView(View):
    """商品详情页"""

    def get(self, request, sku_id):
        """提供商品详情页"""
        # 获取当前sku的信息
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return render(request, '404.html')

        # 查询商品频道分类
        categories = get_categories()
        # 查询面包屑导航
        breadcrumb = get_breadcrumb(sku.category)
        # 查询SKU规格信息
        goods_specs = goods_specs = get_goods_specs(sku)

        # 渲染页面
        context = {
            'categories': categories,
            'breadcrumb': breadcrumb,
            'sku': sku,
            'specs': goods_specs,
        }
        return render(request, 'detail.html', context)


class DetailVisitView(View):
    def post(self, request, category_id):
        try:
            # 1.获取当前的商品
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '缺少必传参数'})
        # 查询 日期数据
        from datetime import date
        # 获取当天日期
        today_data = date.today()
        # 如果有当天的商品分类数据，就累计增加
        try:
            count_data = category.goodsvisitcount_set.get(date=today_data)
        except:
            # 如果没有增加
            count_data = GoodsVisitCount()
        try:
            count_data.count += 1
            count_data.category = category
            count_data.save()
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '新增失败'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 用户浏览记录
class HistoriesView(LoginRequiredJSONMixin, View):
    # 获取
    def get(self, request):
        """获取用户浏览记录"""
        # 获取Redis存储的sku_id列表信息
        redis_conn = get_redis_connection('history')
        sku_ids = redis_conn.lrange('history_%s' % request.user.id, 0, -1)
        print(sku_ids)
        # 根据sku_ids列表数据，查询出商品sku信息
        skus = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url if sku.default_image else "",
                'price': sku.price
            })

        return JsonResponse({'code': 0, 'errmsg': 'OK', 'skus': skus})

    # 保存
    def post(self, request):
        # 获取用户
        user = request.user
        print(request, 'request')
        # 接受参数
        json_dict = json.loads(request.body.decode())
        print(json_dict, 'json_dict')
        sku_id = json_dict.get('sku_id')
        if not sku_id:
            return JsonResponse({'code': 400, 'errmsg': 'sku_id不存在'})
        # 校验参数
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': 'sku不存在'})
        # 保存用户数据
        redis_cli: Redis = get_redis_connection('history')
        # 创建连接
        pl = redis_cli.pipeline()
        print(user.id)
        # 去重
        pl.lrem('history_%s' % user.id, 0, sku_id)
        # 存储
        pl.lpush('history_%s' % user.id, sku_id)
        # 截取5
        pl.ltrim('history_%s' % user.id, 0, 4)
        # 执行命令
        pl.execute()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})
