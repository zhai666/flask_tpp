from celery import Celery
from flask import request, render_template
from flask_mail import Message

import App
from App import dao
from App.helper import getToken
from App.models import User


celery = Celery('tasks',
                broker='redis://127.0.0.1:6379/8',
                include=['manage'])


@celery.task
def sendMail(uId):
    try:
        import manage
    except:
        pass
    global manage
    with manage.app.test_request_context():
        u = dao.getById(User, uId)
        print('查到的用户', u)

        # helper.sendMail(u)

        token = getToken()

        # 将token设置到redis缓存中
        App.ext.cache.set(token, u.id, timeout=10 * 60)  # 允许10分钟内来激活用户

        active_url = request.host_url + 'account/?opt=active&token=' + token

        print(active_url)
        # 发送邮件
        msg = Message(subject='Tpp用户激活',
                      recipients=[u.email],
                      sender='disenqf@163.com')
        msg.html = render_template('msg.html', username=u.name, active_url=active_url)
        try:
            print(msg.html)
            App.ext.mail.send(msg)
            print('邮件已发送')
        except Exception as e:
            print(e)
            print('邮件发送失败')


