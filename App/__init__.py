from flask import Flask

from App import settings
from App.ext import init_ext

def create_app():
    app = Flask(__name__)
    app.config.from_object(settings.Config)

    # 初始化第三方插件
    init_ext(app)

    return app