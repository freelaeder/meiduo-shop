from django.contrib.auth.mixins import LoginRequiredMixin


# 用来验证是否登录的混合类
from django.http import JsonResponse


class LoginRequiredJSONMixin(LoginRequiredMixin):
    def handle_no_permission(self):
        return JsonResponse({'code': 400, 'errmsg': '未登录'})
