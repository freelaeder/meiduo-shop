from decimal import Decimal

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from redis import Redis

from apps.areas.models import Address
from apps.goods.models import SKU
from utils.views import LoginRequiredJSONMixin
from django_redis import get_redis_connection


class OrderView(LoginRequiredJSONMixin, View):
    def get(self, request):
        # 运费
        freight = Decimal(10.00)
        # 用户
        user = request.user
        # 查询当前用户所有的地址
        addresses = Address.objects.filter(user=user, is_deleted=False)
        print(addresses)
        # 获取redis中的购物车数据
        redis_cli: Redis = get_redis_connection('carts')
        # hash 全部
        redis_cart = redis_cli.hgetall('carts_%s' % user.id)
        print(redis_cart)
        # set 选中
        redis_selected = redis_cli.smembers('selected_%s' % user.id)
        print(redis_selected)
        cart = {}
        #  选中的数据
        for sku_id in redis_selected:
            print(int(sku_id), 'sdfsfs')
            cart[int(sku_id)] = int(redis_cart[sku_id])
        # 查询商品信息
        sku_list = []
        skus = SKU.objects.filter(id__in=cart.keys())
        print(skus, 'skus')

        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': cart[sku.id],
                'price': sku.price,
            })

        # 地址
        print(skus, 'end')
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                'id': address.id,
                'province': address.province.name,
                'city': address.city.name,
                'district': address.district.name,
                'place': address.place,
                'receiver': address.receiver,
                'mobile': address.mobile,
            })
        print(addresses_list, 'errr')
        # 构件数据
        context = {
            'addresses': addresses_list,
            'skus': sku_list,
            'freight': freight,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})
