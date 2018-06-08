# 集成第三方
from flask_cache import Cache
from flask_mail import Mail

from App.apis import init_api
from App.models import init_db

mail = Mail()

cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '192.168.43.28',
    'CACHE_REDIS_DB': 12
})


def init_ext(app):
    # 初始化数据库
    init_db(app)

    # 初始化Api接口
    init_api(app)

    # 初始化邮箱模块
    mail.init_app(app)

    # 初始化缓存
    cache.init_app(app)
