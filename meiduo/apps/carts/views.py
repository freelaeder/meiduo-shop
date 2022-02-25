import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
# 是否登录
from redis import Redis

from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin
# redis
from django_redis import get_redis_connection


class CartsView(LoginRequiredJSONMixin, View):
    # 增加
    def post(self, request):
        data_dict = json.loads(request.body)
        print(data_dict)

        sku_id = data_dict.get('sku_id')
        count = data_dict.get('count')
        selected = data_dict.get('selected', True)
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        # 连接redis
        user = request.user
        redis_cli: Redis = get_redis_connection('carts')
        pl = redis_cli.pipeline()
        pl.hincrby('carts_%s' % user.id, sku_id, count)
        if selected:
            pl.sadd('selected_%s' % user.id, sku_id)
        pl.execute()
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    # 获取 展示
    def get(self, request):
        # 获取用户
        user = request.user

        # 连接redis
        redis_cli: Redis = get_redis_connection('carts')
        # 获取hash的数据
        redis_cart = redis_cli.hgetall('carts_%s' % user.id)
        # 获取set的数据
        carts_selected = redis_cli.smembers('selected_%s' % user.id)

        # 根据id查询具体的sku数据

        cart_dict = {}
        # {'skuid1':{'count':10,'selected':True},'skuid2':{'count':3,'selected':False}}
        for sku_id, count in redis_cart.items():
            # sku_if 和 count 当前是bytes类型,直接转为int
            cart_dict[int(sku_id)] = {
                'count': int(count),
                'selected': sku_id in carts_selected
            }
        # 获取所有的sku——id
        sku_ids = redis_cart.keys()
        cart_skus = []
        skus = SKU.objects.filter(id__in=sku_ids)

        for sku in skus:
            cart_skus.append({
                'name': sku.name,  # 名字
                'default_image_url': sku.default_image.url,  # 图片
                'price': sku.price,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': cart_dict.get(sku.id).get('selected'),
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})
