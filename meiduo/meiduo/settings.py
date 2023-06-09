"""
Django settings for meiduo project.

Generated by 'django-admin startproject' using Django 2.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '%foq2kx$rcb8300@(h!py#z4=q*w-29yd@yad&3^!%@gs#z9!2'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# 添加可允许访问的ip，域名
ALLOWED_HOSTS = ['www.meiduo.site', '127.0.0.1', '0.0.0.0', '192.168.232.128']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 添加apps下的users 注意
    'apps.users',
    # 添加跨域
    'corsheaders',
    # 添加 图形验证
    'apps.verifications',
    # 添加QQ应用
    'apps.oauth',
    # 添加地区
    'apps.areas',
    # '添加 ad 广告'
    'apps.ad',
    # 添加商品
    'apps.goods',
    # 搜索
    'haystack',
    # 定时任务
    'django_crontab',
    # 购物车
    'apps.carts',
    # 订单
    'apps.ordes',
    # 添加支付
    'apps.payment',
    # 添加后台管理
    'apps.meiduo_admin',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # post 会有保护，所以注释掉
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 跨域请求解决
    'corsheaders.middleware.CorsMiddleware'

]

ROOT_URLCONF = 'meiduo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [BASE_DIR / 'templates']
        #   'DIRS': [BASE_DIR / 'templates']
        # TypeError: unsupported operand type(s) for /: 'str' and 'str'
        # 修改为
        # 'DIRS': [str.format(BASE_DIR, '/templates')]
        'DIRS': [os.path.join(BASE_DIR, "templates"), ]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'meiduo.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '127.0.0.1',
        'PORT': 3306,  # 数据库端口
        'USER': 'free',  # 数据库用户名
        'PASSWORD': '926400',  # 数据库用户密码
        'NAME': 'meidb'  # 数据库名字
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

CACHES = {
    "default": {  # 默认
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.232.128:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "session": {  # session
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.232.128:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "code": {  # code 图形验证码
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.232.128:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "history": {  # code 用户浏览记录
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.232.128:6379/3",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "carts": {  # code 购物车
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://192.168.232.128:6379/4",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },

}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "session"
# 日志
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  # 是否禁用已经存在的日志器
    'formatters': {  # 日志信息显示的格式
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {  # 对日志进行过滤
        'require_debug_true': {  # django在debug模式下才输出日志
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {  # 日志处理方法
        'console': {  # 向终端中输出日志
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {  # 向文件中输出日志
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/meiduo.log'),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {  # 日志器
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],  # 可以同时向终端与文件中输出日志
            'propagate': True,  # 是否继续传递日志信息
            'level': 'INFO',  # 日志器接收的最低日志级别
        },
    }
}

# 替换django自带的用户模型
AUTH_USER_MODEL = 'users.User'

# 添加跨域白名单
# CORS
CORS_ORIGIN_WHITELIST = (
    'http://127.0.0.1:8080',
    'http://127.0.0.1:8090',
    'http://localhost:8080',
    'http://www.meiduo.site:8080',
    'http://www.meiduo.site:8000',
    'http://www.meiduo.site:8090',

)
CORS_ALLOW_CREDENTIALS = True  # 允许携带cookie

# 添加邮箱 验证
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.126.com'
EMAIL_PORT = 25
# 发送邮件的邮箱
EMAIL_HOST_USER = 'freelaeder@126.com'
# 在邮箱中设置的客户端授权密码
EMAIL_HOST_PASSWORD = 'GJOWWLVYFUWUHATO'
# 收件人看到的发件人
EMAIL_FROM = 'freelaeder@126.com'

# 邮箱验证链接
EMAIL_VERIFY_URL = 'http://www.meiduo.site:8080/success_verify_email.html'

# 微博登录参数
# 我们申请的 客户端id
WEIBO_CLIENT_ID = '1319853025'
# 我们申请的 客户端秘钥
WEIBO_CLIENT_SECRET = '23d5c0f50c838585a8d8b23259318e29'
# 我们申请时添加的: 登录成功后回调的路径
WEIBO_REDIRECT_URI = 'http://www.meiduo.com:8080/oauth_callback.html'

# 指定自定义的Django文件存储类
DEFAULT_FILE_STORAGE = 'utils.fastdfs.storage.FastDFSStorage'

# FastDFS相关参数
FDFS_BASE_URL = 'http://192.168.232.128:8888/'

# Haystack
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://192.168.232.128:9200/',  # Elasticsearch服务器ip地址，端口号固定为9200
        'INDEX_NAME': 'meiduo_index',  # Elasticsearch建立的索引库的名称
    },
}

# 当添加、修改、删除数据时，自动生成索引
# HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

# 每页返回的条数
HAYSTACK_SEARCH_RESULTS_PER_PAGE = 5

CRONJOBS = [
    # 每1分钟生成一次首页静态文件
    ('*/1 * * * *', 'apps.goods.crons.generate_static_index_html', '>> ' + os.path.join(BASE_DIR, 'logs/crontab.log'))
]

# 支付宝sdk
ALIPAY_APPID = '2021000119627777'
ALIPAY_DEBUG = True
ALIPAY_URL = 'https://openapi.alipaydev.com/gateway.do'
ALIPAY_RETURN_URL = 'http://www.meiduo.site:8080/pay_success.html'
APP_PRIVATE_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/app_private_key.pem')
ALIPAY_PUBLIC_KEY_PATH = os.path.join(BASE_DIR, 'apps/payment/keys/alipay_public_keu.pem')

# 配置drf
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
        # 'rest_framework.authentication.BasicAuthentication',
    ),
}
import datetime

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'apps.meiduo_admin.utils.jwt_response_payload_handler'
}
