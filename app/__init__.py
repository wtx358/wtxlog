# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask.ext.themes import setup_themes
from flask.ext.mobility import Mobility
from config import config
from ext import cache, db, mail, login_manager
from models import User, AnonymousUser

# 默认是basic, strong这个强度在BAE3下造成登陆几秒之后就退出的现象
# 而JAE,SAE上不会出现, 也有可能是应用引擎环境的问题, 暂时使用默认值
#login_manager.session_protection = 'strong'
login_manager.login_view = 'account.login'
login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_appconfig():
    _env = os.getenv('SERVER_SOFTWARE')
    if _env: 
        if _env.startswith('bae'):
            env = 'bae'
        elif _env.startswith('direwolf'):
            env = 'sae'
        else:
            env = 'production'
    else:
        env = 'local'
    return env


def create_app(config_name):
    app = Flask(__name__)
    app.config['APPENV'] = str(get_appconfig())
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    cache.init_app(app)
    db.init_app(app)
    db.app = app
    login_manager.init_app(app)
    mail.init_app(app)
    setup_themes(app)
    Mobility(app)

    from .utils.filters import register_filters
    register_filters(app)

    from .utils.processors import utility_processor 
    app.context_processor(utility_processor)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .account import account as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/account')

    from .admins import admin
    admin.init_app(app)

    # 暂时解决因Gunicorn中引发ERROR 11而无法正常提交的问题
    @app.teardown_request
    def teardown_request(response_or_exc):
        if app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN']:
            try:
                db.session.commit()
            except:
                db.session.rollback()
        db.session.remove()

    return app
