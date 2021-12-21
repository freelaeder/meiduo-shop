from django.urls import path
from apps.verifications.views import *

urlpatterns = [
    # 验证 this.host + "/image_codes/" + this.image_code_id + "/"
    # 返回图形验证码 get
    path('image_codes/<uuid:uuid>/', ImageCodeView.as_view()),
    # 验证短信  图形验证码 get
    # this.host + '/sms_codes/' + this.mobile + '/' + '?image_code=' +
    # this.image_code + '&image_code_id=' + this.image_code_id
    path('sms_codes/<mobile:mobile>/', SmsCodeView.as_view()),


]
