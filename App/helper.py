# 自定义工具类
import hashlib
import uuid

from flask import request, render_template
from flask_mail import Message

import App


def md5_crypt(txt):
    m = hashlib.md5()
    m.update(txt.encode())

    return m.hexdigest()


def getToken():
    return md5_crypt(str(uuid.uuid4()))


def sendEmail(u):
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
        App.ext.mail.send(msg)
    except Exception as e:
        print(e)
        print('邮件发送失败')