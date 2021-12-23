from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from meiduo import settings
from django import http
from django.conf import settings
from django.views import View
from QQLoginTool.QQtool import OAuthQQ
import logging

logger = logging.getLogger('django')


class QQAuthURLView(View):
    def get(self, request):
        """Oauth2.0认证"""

        return JsonResponse({'code': 0, 'errmsg': 'OK',})
