# -*- coding:utf-8 -*-

from manage import app

from bae.core.wsgi import WSGIApplication
application = WSGIApplication(app, stderr='log')
