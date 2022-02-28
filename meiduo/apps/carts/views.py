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
            print('selected_%s'%user.id)
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
                'id': sku.id,
                'name': sku.name,  # 名字
                'default_image_url': sku.default_image.url,  # 图片
                'price': sku.price,
                'count': cart_dict.get(sku.id).get('count'),
                'selected': cart_dict.get(sku.id).get('selected'),
            })
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})

    def put(self, request):

        # 接受参数

        data_dict = json.loads(request.body)
        print(data_dict, 'put')
        sku_id = data_dict.get('sku_id')
        count = data_dict.get('count')
        selected = data_dict.get('selected')
        # 校验
        if not all([sku_id, count]):
            return JsonResponse({'code': 400, 'errmsg': '缺少必要参数'})

        try:
            sku = SKU.objects.get(id=sku_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '没有该商品'})
        try:
            count = int(count)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '参数counterr'})
        user = request.user
        print(user, 'put')
        redis_cli: Redis = get_redis_connection('carts')
        pl = redis_cli.pipeline()

        pl.hset('carts_%s' % user.id, sku_id, count)
        if selected:
            pl.sadd('selected_%s' % user.id, sku_id)
        else:
            pl.srem('selected_%s' % user.id, sku_id)
        # 执行
        pl.execute()
        cart_sku = {
            'count': count,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_sku': cart_sku})

    # 删除

    def delete(self, request):
        # 获取参数
        data_dict = json.loads(request.body)
        print(data_dict)
        sku_id = data_dict.get('sku_id')
        if not all([sku_id]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        try:
            SKU.objects.get(id=sku_id)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '没有该商品'})
        user = request.user
        redis_cli: Redis = get_redis_connection('carts')
        # 创建管道
        pl = redis_cli.pipeline()
        # 删除键，等于删除整条数据
        pl.hdel('carts_%s' % user.id, sku_id)
        pl.srem('selected_%s' % user.id, sku_id)
        # 执行
        pl.execute()

        return JsonResponse({'code': 0, 'errmsg': 'ok'})
        pass


# 购物车全选
class CartSelectView(LoginRequiredJSONMixin, View):
    def put(self, request):
        # 接受参数
        data_dict = json.loads(request.body)
        print(data_dict)
        selected = data_dict.get('selected')
        if selected:
            if not isinstance(selected, bool):
                return JsonResponse({'code': 400, 'errmsg': ''})
        # user
        user = request.user
        redis_cli = get_redis_connection('carts')
        cart = redis_cli.hgetall('carts_%s' % user.id)
        sku_id_list = cart.keys()
        if selected:
            # 全选
            redis_cli.sadd('selected_%s' % user.id, *sku_id_list)
        else:
            # 取消全选
            redis_cli.srem('selected_%s' % user.id, *sku_id_list)
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


# 展示简单购物车
class CartSimpleView(LoginRequiredJSONMixin, View):
    def get(self, request):
        user = request.user
        # 连接redis
        redis_cli = get_redis_connection('carts')

        redis_cart = redis_cli.hgetall('carts_%s' % user.id)
        cart_selected = redis_cli.smembers('selected_%s' % user.id)
        print(redis_cart, 'redis_cart')
        print(cart_selected)
        cart_dict = {}
        for sku_id, count in redis_cart.items():
            cart_dict[int(sku_id)] = {
                'count': int(count),
                'selected': sku_id in cart_selected,
            }
        #  获取所有的sku_id
        sku_ids = redis_cart.keys()
        cart_skus = []
        skus = SKU.objects.filter(id__in=sku_ids)
        # 拼接数据
        for sku in skus:
            cart_skus.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': cart_dict.get(sku.id).get('count'),

            })

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'cart_skus': cart_skus})
