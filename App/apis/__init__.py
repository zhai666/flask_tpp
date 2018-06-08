from flask_restful import Api

from App.apis.account import AccountApi
from App.apis.city import CityApi
from App.apis.movies import MovieApi
from App.apis.user import UserApi

api = Api()  # 创建RESTful的Api对象


def init_api(app):
    api.init_app(app)


# 向api接口中添加资源(Resource)
api.add_resource(CityApi, '/city/')
api.add_resource(UserApi, '/user/')
api.add_resource(AccountApi, '/account/')
api.add_resource(MovieApi, '/movies/')