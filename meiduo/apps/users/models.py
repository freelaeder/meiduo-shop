from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    mobile = models.CharField(max_length=11, unique=True)
    # 添加邮箱字段
    email_active = models.BooleanField(default=False, verbose_name='邮箱验证状态')
    default_address = models.IntegerField(null=True, blank=True, verbose_name='默认地址')

    class Meta:
        db_table = 'tb_users'
        verbose_name = '用户管理'
        verbose_name_plural = verbose_name
