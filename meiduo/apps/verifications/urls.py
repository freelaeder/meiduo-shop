from django.urls import path
from apps.verifications.views import *

urlpatterns = [
    # 验证 this.host + "/image_codes/" + this.image_code_id + "/"
    # 图形验证码 get请求
    path('image_codes/<uuid>/', ImageCodeView.as_view())

]
