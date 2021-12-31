import json

from django.contrib.auth import logout
from django.core.cache import cache
from django.http import JsonResponse, HttpResponse
from django.views import View
from apps.areas.models import *
from utils.views import LoginRequiredJSONMixin
import re


class AreasView(View):
    def get(self, request):
        # 1. 获取cache
        province_list = cache.get('provinces')
        if not province_list:
            print('没有缓存')

            # 去数据库查询所有的省份数据
            try:
                areas = Area.objects.filter(parent=None)
            except Exception as e:
                print(e)
                return JsonResponse({'code': 400, 'errmsg': '数据库异常'})

                # 添加省的数据
            province_list = []
            for a in areas:
                province_list.append({'id': a.id, 'name': a.name})
            # 保存 provinces 在 redis
            cache.set('provinces', province_list, 3600 * 24 * 30)

        # 返回
        return JsonResponse({'code': 0, 'province_list': province_list})


# 获取省下的市
class SubAreasView(View):
    def get(self, request, area_id):
        # 添加缓存
        subs = cache.get('sub_%s' % area_id)
        if not subs:

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
            # 添加 缓存
            cache.set('sub_%s' % area_id, subs, 3600 * 24 * 30)
        return JsonResponse({'code': 0, 'sub_data': {'subs': subs}})


class AddresView(View):
    # 添加地址
    def post(self, request):
        # 获取数据
        body = request.body
        data_dict = json.loads(body)
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        district_id = data_dict.get('district_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')
        # 检验完整
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 400, 'errmsg': '参数不够'})
        # 添加数据
        try:
            address = Address.objects.create(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                mobile=mobile,
                tel=tel,
                email=email,
                place=place,
            )
            # 设置address 为默认地址
            request.user.default_address = address.id
            # 保存
            request.user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'errmsg': '保存失败'})
        address_dict = {
            'id': address.id,
            'title': address.title,
            'receiver': address.receiver,
            'city': address.city.name,
            'province': address.province.name,
            'district': address.district.name,
            'place': address.place,
            'mobile': address.mobile,
            'tel': address.tel,
            'email': address.email
        }
        # 返回
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})

    # 展示地址
    def get(self, request):
        # 获取所有的用户对象
        user = request.user
        # 获取所有地址
        try:
            # addresses =Address.objects.filter(user=user)
            # models.  related_name='addresses'
            addresses = user.addresses.all()
            # 存地址
            address_dict_list = []
            # 循环添加数据
            for address in addresses:
                address_dict = {
                    "id": address.id,
                    "title": address.title,
                    "receiver": address.receiver,
                    "province": address.province.name,
                    "city": address.city.name,
                    "district": address.district.name,
                    "place": address.place,
                    "mobile": address.mobile,
                    "tel": address.tel,
                    "email": address.email
                }
                # 拼接列表
                address_dict_list.insert(0, address_dict)

        except Exception as e:
            print(e)
            return JsonResponse({'code': 501, 'errmsg': '查询失败'})

        return JsonResponse({'code': 0, 'errmsg': 'ok', 'addresses': address_dict_list,
                             'default_address_id': request.user.default_address})


class DefaultView(View):
    # 设置为默认地址
    def put(self, request, did):
        # did ->前段传递的点击的Address did
        print(did)
        try:
            # 此时 request.uesr.id 是mysql 中 tb_users 表中的id
            # 因为在mysql中tb_address 有user_id 是 关联的 tb_users 的id
            print(request.user.id)
            User.objects.filter(id=request.user.id).update(default_address=did)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 1, 'errmsg': 'err'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class AdrressSetView(LoginRequiredJSONMixin, View):
    # 删除地址
    def delete(self, request, did):
        try:
            Address.objects.filter(id=did).delete()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 1, 'errmsg': '删除失败'})

        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    # 修改地址
    def put(self, request, did):
        # did 就是用户传递的 id
        body = request.body
        data_dict = json.loads(body)
        # {'id': 2, 'title': 'freelaeder',
        # 'receiver': 'freelaeder',
        # 'province': '广西壮族自治区', 'city': '南宁市', 'district': '兴宁区',
        # 'place': '兔兔小区', 'mobile': '18916216441', 'tel': '12330-1231231',
        # 'email': 'freelader@123.com', 'province_id': 220000,
        # 'city_id': 220200, 'district_id': 220204}
        # 获取数据
        receiver = data_dict.get('receiver')
        province_id = data_dict.get('province_id')
        city_id = data_dict.get('city_id')
        place = data_dict.get('place')
        mobile = data_dict.get('mobile')
        tel = data_dict.get('tel')
        email = data_dict.get('email')
        district_id = data_dict.get('district_id')
        # 校验完整
        if not all([receiver, province_id, city_id, district_id, place, mobile]):
            return JsonResponse({'code': 1, 'errmsg': '参数不够'})
        #
        if not re.match(r'^1[3-9]\d{9}$', mobile):
            return JsonResponse({'code': 400,
                                 'errmsg': '参数mobile有误'})

        # if tel:
        #     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
        #         return JsonResponse({'code': 400,
        #                                   'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400,
                                     'errmsg': '参数email有误'})
        # 判断地址是否存在 并更新
        try:
            Address.objects.filter(id=did).update(
                user=request.user,
                title=receiver,
                receiver=receiver,
                province_id=province_id,
                city_id=city_id,
                district_id=district_id,
                place=place,
                mobile=mobile,
                tel=tel,
                email=email
            )
        except Exception as e:
            print(e)
            return JsonResponse({'code': 1, 'errmsg': '更新失败'})

            # 构造响应数据
        address = Address.objects.get(id=did)
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }

        # 响应更新地址结果
        return JsonResponse({'code': 0, 'errmsg': '更新地址成功', 'address': address_dict})


class TitleView(LoginRequiredJSONMixin, View):
    #   修改title
    def put(self, request, did):
        # 获取用户传递要修改的id
        print(did)
        body = request.body
        data_dict = json.loads(body)
        # 要修改的title
        title = data_dict.get('title')
        # 更新
        res = Address.objects.filter(id=did).update(title=title)

        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class PasswordView(LoginRequiredJSONMixin, View):
    # 修改密码
    def put(self, request):
        # 获取参数
        data_dict = json.loads(request.body.decode())
        print(data_dict)
        # {'old_password': 'jdasjfljalfdsa',
        # 'new_password': '926400lo',
        # 'new_password2': '926400lo'}
        # 校验参是否完整
        old_password = data_dict.get('old_password')
        new_password = data_dict.get('new_password')
        new_password2 = data_dict.get('new_password2')
        if not all([old_password, new_password, new_password2]):
            return JsonResponse({'code': 1, 'errmsg': '参数不够'})
        # 校验两次的新密码是否一致
        if new_password != new_password2:
            return JsonResponse({'code': 1, 'errmsg': '密码不一致'})

        # 获取旧密码
        result = request.user.check_password(old_password)
        if not result:
            return JsonResponse({'code': 1, 'errmsg': '旧密码错误'})

        if not re.match(r'^[0-9A-Za-z]{8,20}$', new_password):
            return JsonResponse({'code': 400, 'errmsg': '密码最少8位,最长20位'})

        # 修改密码
        try:
            request.user.set_password(new_password)
            request.user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 1, 'errmsg': '修改失败'})
        # 清理状态保持
        logout(request)
        response = JsonResponse({'code': 0, 'errmsg': 'ok'})
        response.delete_cookie('username')

        return response
