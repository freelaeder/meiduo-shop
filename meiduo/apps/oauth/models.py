from django.db import models

# Create your models here.
from django.db import models
# 这是一个基类
from utils.models import BaseModel


class OAuthQQUser(BaseModel):
    """weibo登录用户数据"""
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, verbose_name='用户')

    # db_index=True添加索引
    access_token = models.CharField(max_length=64, verbose_name='access_token', db_index=True)

    class Meta:
        db_table = 'tb_oauth_weibo'
        verbose_name = '微博登录用户数据'
        verbose_name_plural = verbose_name
