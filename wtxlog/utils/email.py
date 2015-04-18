from threading import Thread
from flask import current_app
from flask.ext.mail import Message
from ..ext import mail
from .helpers import render_template


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message('%s %s' % (app.config['APP_MAIL_SUBJECT_PREFIX'], subject),
                  sender=app.config['APP_MAIL_SENDER'], recipients=[to])
    msg.body = render_template('%s.txt' % template, **kwargs)
    msg.html = render_template('%s.html' % template, **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
