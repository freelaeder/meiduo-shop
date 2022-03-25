from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from apps.goods.models import SKUImage, SKU

# sku图片
from apps.meiduo_admin.serializers.image import SKUImageSerializer, SKUSerializer
from apps.meiduo_admin.utils import PageNum


class SKUImageView(ModelViewSet):
    # 指定 queryset
    queryset = SKUImage.objects.all()
    # 序列化器
    serializer_class = SKUImageSerializer
    # 分页
    pagination_class = PageNum

    # 重写保存图片
    def create(self, request, *args, **kwargs):
        # - 1 接收参数 校验
        sku_id = request.data.get('sku')
        image = request.FILES.get('image')
        print(request.data)
        print(image)
        # - 2 把图片上传到fastdfs里 返回一个图片地址
        from fdfs_client.client import Fdfs_client
        # 创建FastDFS连接对象
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 上传
        result = client.upload_by_buffer(image.read())
        print(result)
        # {'Group name': 'group1',
        # 'Remote file_id': 'group1/M00/00/02/wKjogGI9ekuAQQuJAAB5NgRRAsI7903342',
        # 'Status': 'Upload successed.',
        # 'Local file name': '',
        # 'Uploaded size': '30.00KB',
        # 'Storage IP': '192.168.232.128'}
        # 判断是否成功 不等于返回
        if result.get('Status') != 'Upload successed.':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # 获取地址
        imgage_url = result.get('Remote file_id')
        # 创建数据
        SKUImage.objects.create(sku_id=sku_id, image=imgage_url)
        # 返回响应
        return Response(status=status.HTTP_201_CREATED)

    # 重写update  更新数据
    def update(self, request, *args, **kwargs):
        # 创建fdfs
        from fdfs_client.client import Fdfs_client
        client = Fdfs_client('utils/fastdfs/client.conf')
        # 获取数据
        # print(request.data)
        # <QueryDict: {'sku': ['3'], 'image': [<InMemoryUploadedFile: 30.png (image/png)>]}>
        # print(kwargs)
        # {'pk': '45'}
        # 获取pk
        pks = kwargs.get('pk')
        # 获取图片
        images = request.FILES.get('image')
        # 上传图片到fastdfs
        res = client.upload_by_buffer(images.read())
        # 判断是否成功 不等于返回
        if res.get('Status') != 'Upload successed.':
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        # 获取地址
        imgage_url = res.get('Remote file_id')
        print(imgage_url, 'image_url')
        # 获取sku_id
        sku_id = request.data.get('sku')
        # 查询图片对象
        update_img = SKUImage.objects.get(id=pks)
        # 更新数据
        update_img.image = imgage_url
        update_img.sku_id = sku_id
        update_img.save()
        # 返回响应
        return Response(status=status.HTTP_201_CREATED)

    # 重写删除 彻底删除
    def destroy(self, request, *args, **kwargs):
        # 获取删除的skuimage id
        pks = kwargs.get('pk')
        # 获取 删除的字段
        del_img = SKUImage.objects.get(id=pks)
        # 删除的fields_id
        field = del_img.image.url
        # 截取
        print(field[28:])
        del_url = field[28:]
        # 连接fastdfs
        from fdfs_client.client import Fdfs_client
        client = Fdfs_client('utils/fastdfs/client.conf')
        res = client.delete_file(del_url)
        # 删除数据库
        del_img.delete()
        return Response(status=status.HTTP_201_CREATED)


# skus/simple/ 返回新增商品时的商品id
class SkuImage(APIView):
    def get(self, request):
        data = SKU.objects.all()
        # 指定序列化器
        ser = SKUSerializer(data, many=True)
        return Response(ser.data)
