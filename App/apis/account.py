from datetime import datetime
from flask import request, session
from flask_restful import Resource, reqparse, fields, marshal
import App.ext
from App import dao, helper
from App.models import User


class AccountApi(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('opt', required=True, help='没有声明opt的操作')

    def get(self):
        # 从请求参数中获取opt和token参数值
        # 如果opt 为active ，则从redis缓存中查询token对应的user.id
        # 再通过 user.id查询数据库中用户， 最后更新用户的is_active状态为True
        args = self.parser.parse_args()
        opt = args.get('opt')
        if opt == 'active':
            activeParser = self.parser.copy()
            activeParser.add_argument('token', required=True, help='必须提供激活的token')
            args = activeParser.parse_args()  # 验证请求参数
            token = args.get('token')
            # 进一步处理
            user_id = App.ext.cache.get(token)
            if user_id:
                # 查询用户，并设置用户激活状态
                user = dao.getById(User, user_id)
                user.is_active = True

                dao.save(user)

                return {'msg': user.nickName+' 用户激活成功!'}

            else:
                # 重新申请用户激活
                reactive_url = request.host_url + 'account/?opt=reactive'
                return {'msg': ' 本次激活已过期，需要重新申请激活: '+ reactive_url}
        elif opt == 'login':
            return self.login()
        elif opt == 'reactive':
            return self.reactive()
        elif opt == 'logout':
            return self.logout()

    def login(self):  # GET请求时，opt为login时
        loginParser = self.parser.copy()
        loginParser.add_argument('name', required=True, help='用户登录必须提供用户名')
        loginParser.add_argument('passwd', required=True, help='用户登录必须提供口令')

        # 验证登录参数
        args = loginParser.parse_args()

        username = args.get('name')
        password = args.get('passwd')

        # 查询用户(额外添加一条件：用户已激活)
        print(username, password)
        qs = dao.query(User).filter(User.name.__eq__(username),
                               User.password.__eq__(helper.md5_crypt(password)),
                               User.is_active == True,
                                    User.is_life == True)

        if not qs.count():
            return {'status': 600, 'msg': '用户登录失败，用户名或口令不正确！'}

        u = qs.first()

        u.last_login_time = datetime.today()

        dao.save(u)  # 更新用户登录的时间

        token = helper.getToken()
        session[token] = u.id  # 将token存放session中

        out_user_fields = {
            'name': fields.String,
            'email': fields.String,
            'phone': fields.String,
            'photo': fields.String(attribute='photo_1')
        }

        out_fields = {
            'msg': fields.String,
            'data': fields.Nested(out_user_fields),
            'access_token': fields.String
        }

        data = {'msg': '登录成功!',
                'data': u,
                'access_token': token}

        # 通过marshal 将返回的data数据按输出字段转成json字符
        return marshal(data, out_fields)

    def reactive(self):
        # 重新申请用户激活
        reactiveParser = self.parser.copy()
        reactiveParser.add_argument('email', required=True, help='必须提供用户邮箱')
        args = reactiveParser.parse_args()

        email = args.get('email')
        qs = dao.query(User).filter(User.email.__eq__(email))
        if not qs.count():
            return {
                'status': 700,
                'msg': email + ' 邮箱未被注册！'
            }

        # 重新发送邮箱
        helper.sendEmail(qs.first())

        return {'msg':'重新申请用户激活，请查收邮箱进行激活'}

    def logout(self):
        myParser = self.parser.copy()
        myParser.add_argument('token', required=True, help='用户退出必须提供token参数')

        args = myParser.parse_args()
        token = args.get('token')
        user_id = session.get(token)
        if not user_id:
            return {'status': 701, 'msg': '用户未登录，请先登录!'}

        u = dao.getById(User, user_id)
        if not u:
            return {'status': 702, 'msg': '用户退出失败，token无效!'}

        session.pop(token)  # 从session中删除token
        return {'status': 200, 'msg': '退出成功!'}

