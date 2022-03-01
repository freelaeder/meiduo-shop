import http
import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from redis import Redis

from apps.areas.models import Address
from apps.goods.models import SKU
from apps.ordes.models import OrderInfo, OrderGoods
from utils.views import LoginRequiredJSONMixin
from django_redis import get_redis_connection


# 订单展示
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
        # 构件数据
        context = {
            'addresses': addresses_list,
            'skus': sku_list,
            'freight': freight,
            'default_address_id': request.user.default_address,
        }
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'context': context})


# 提交订单
class CommitView(LoginRequiredJSONMixin, View):
    def post(self, request):
        # 获取参数
        data_dict = json.loads(request.body)
        print(data_dict)
        address_id = data_dict.get('address_id')
        pay_method = data_dict.get('pay_method')
        # 校验参数完整
        if not all([address_id, pay_method]):
            return JsonResponse({'code': 400, 'errmsg': '缺少参数'})
        # 判断address_id 是否存在
        try:
            address = Address.objects.get(id=address_id)
        except Exception as e:
            return JsonResponse({'code': 400, 'errmsg': '地址不存在'})
            # 判断pay_method是否合法
        if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
            return http.HttpResponseBadRequest('参数pay_method错误')

        # 保存订单对象
        user = request.user
        # 生成订单编号：年月日时分秒+用户编号
        order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
        print(order_id, 'order_id')
        # 开启事务
        with transaction.atomic():
            # 创建事务回滚点
            save_id = transaction.savepoint()
            try:
                # 生产顶单表
                order = OrderInfo.objects.create(
                    order_id=order_id,
                    user=user,
                    address=address,
                    total_count=0,  # 商品数量
                    total_amount=0,  # 商品总金额
                    freight=Decimal('10.00'),
                    pay_method=pay_method,
                    status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
                        'ALIPAY'] else
                    OrderInfo.ORDER_STATUS_ENUM['UNSEND'],
                )
                # 过滤勾选的商品
                redis_cli: Redis = get_redis_connection('carts')
                # 获取全部数据 hash
                redis_carts = redis_cli.hgetall('carts_%s' % user.id)
                print(redis_carts, 'redis_carts')
                # 获取set 选中的数据
                carts_selected = redis_cli.smembers('selected_%s' % user.id)
                print(carts_selected, 'carts_selected')
                # 把选中的sku 数据放到新的字典中，值是他的数量
                cart_data = {}
                for sku_id in carts_selected:
                    cart_data[int(sku_id)] = int(redis_carts[sku_id])
                # 遍历所有的商品id
                sku_ids = cart_data.keys()
                print(sku_ids, 'sku_ids')
                for sku_id in sku_ids:
                    while True:
                        # 查询sku信息
                        sku = SKU.objects.get(id=sku_id)
                        # 读取原始的库存
                        # 库存
                        orgin_stock = sku.stock
                        # 销量
                        orgin_sales = sku.sales
                        # 判断库存
                        sku_count = cart_data[sku.id]
                        if sku_count > sku.stock:
                            # 出错回滚
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'code': 400, 'errmsg': '库存不足呦'})
                        # # sku 库存减少，销量增加
                        # sku.stock -= sku_count
                        # sku.sales += sku_count
                        # sku.save()

                        # 乐观锁
                        new_stock = orgin_stock - sku_count
                        new_sales = orgin_sales + sku_count
                        result = SKU.objects.filter(id=sku_id, stock=orgin_stock).update(stock=new_stock,
                                                                                         sales=new_sales)
                        if result == 0:
                            continue
                        # 保存订单信息 OrderGoods
                        OrderGoods.objects.create(
                            order=order,
                            sku=sku,
                            count=sku_count,
                            price=sku.price,
                        )
                        # 把sku的价格累计加到订单对象里
                        order.total_count += sku_count
                        order.total_amount += (sku_count * sku.price)

                        # 下单成功或失败跳出循环
                        break
                # 总价加上运费
                order.total_amount += order.freight
                order.save()
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                return JsonResponse({'code': 400, 'errmsg': '下单失败'})
            # 提交成功，显示提交事务
            transaction.savepoint_commit(save_id)
        # 清空购物车
        pl = redis_cli.pipeline()
        pl.hdel('carts_%s' % user.id, *carts_selected)
        pl.srem('selected_%s' % user.id, *carts_selected)
        # 执行
        pl.execute()

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'order_id': order.order_id})
