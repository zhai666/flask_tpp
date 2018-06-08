from flask import request, session
from flask_restful import Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import BaseQuery

from App import dao
from App.models import Movies, User, Qx
from App.settings import QX


def check_login(qx):
    def check(fun):
        def wrapper(*args, **kwargs):
            print('-check login--')
            token = request.args.get('token')
            user_id = session.get(token)
            if not user_id:
                return {'msg': '用户必须先登录'}

            loginUser = dao.getById(User, user_id)
            if loginUser.rights & qx == qx:
                return fun(*args, **kwargs)
            else:
                qxObj = dao.query(Qx).filter(Qx.right == qx).first()
                return {'msg': '用户没有 {} 权限'.format(qxObj.name)}

        return wrapper

    return check


class MovieApi(Resource):
    # 定制输入参数
    parser = reqparse.RequestParser()
    parser.add_argument('flag', type=int, required=True, help='必须指定影片类型')
    parser.add_argument('city', default='')
    parser.add_argument('region', default='')
    parser.add_argument('orderby', default='openday')
    parser.add_argument('sort', type=int, default=1)  # 1 降序 0 升序
    parser.add_argument('page', type=int, default=1, help='页码必须是数值')
    parser.add_argument('limit', type=int, default=10, help='每页显示的大小必须是数值')

    # 定制输出字段
    out_fields = {
        'returnCode': fields.String(default='0'),
        'returnValue': fields.Nested({
            'backgroundPicture': fields.String(attribute='backgroundpicture'),
            'country': fields.String,
            'director': fields.String,
            'showName': fields.String(attribute='showname'),
            'showNameEn': fields.String(attribute='shownameen'),
            'openTime': fields.DateTime(attribute='openday', dt_format='%Y-')
        })
    }

    @marshal_with(out_fields)
    def get(self):
        # 验证请求参数
        args = self.parser.parse_args()
        qs: BaseQuery = dao.query(Movies).filter(Movies.flag == args.get('flag'))

        sort = args.get('sort')
        qs: BaseQuery = qs.order_by(('-' if sort == 1 else '') + args.get('orderby'))

        # 分页
        pager = qs.paginate(args.get('page'), args.get('limit'))

        print('获取的总影片数：', len(qs.all()))
        return {"returnValue": pager.items}

    # http://127.0.0.1:8000/movies/?token=dbe3a71e3c77f8a523cbd6930d81afc5&mid=6922

    @check_login(QX.DELETE_QX)
    def delete(self):
        mid = request.args.get('mid')
        movie = dao.getById(Movies, mid)
        if not movie:
            return {'msg': '你要删除的影片资源不存在！'}

        dao.delete(movie)
        return {'msg': '删除成功'}
    # 从session中获取登录用户的token
    # user_id = session.get(request.args.get('token'))
    # if not user_id:
    #     return {'msg': '请先登录!'}
    #
    # loginUser:User = dao.getById(User, user_id)
    #
    # # 删除影片功能
    # if loginUser.rights & QX.DELETE_QX == QX.DELETE_QX:
    #     # 当前用户有删除权限
    #     movie = dao.getById(Movies, mid)
    #     if not movie:
    #         return {'msg': '你要删除的影片资源不存在！'}
    #
    #     dao.delete(movie)
    #     return {'msg': '删除成功'}
    #
    # return {'msg': '对不起，你没有此权限，请及时联系管理员'}
