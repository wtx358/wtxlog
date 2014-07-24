# -*- coding: utf-8 -*-

import os
import logging
from hashlib import md5

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    THEME = 'imtx'
    SITE_NAME = u'wtxlog'

    # 是否启用博客模式
    BLOG_MODE = True

    BODY_FORMAT = 'html' # html or markdown

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_POOL_RECYCLE = 10

    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    # gmail的话带下面那行的注释去掉
    #MAIL_USE_TLS = True
    # qq企业邮箱的话带下面那行的注释去掉
    #MAIL_USE_SSL = True

    APP_MAIL_SUBJECT_PREFIX = '[%s]' % SITE_NAME
    APP_MAIL_SENDER = '%s Admin <%s>' % (SITE_NAME, MAIL_USERNAME)
    APP_ADMIN = os.environ.get('APP_ADMIN')

    # cache keys
    _PREFIX = md5(SECRET_KEY).hexdigest()[7:15]
    MEMCACHE_KEY = _PREFIX + '_view_%s'
    STATIC_KEY = _PREFIX + '_static_%s'

    # QiNiu Cloud Storage
    QINIU_AK = os.environ.get('QINIU_AK')
    QINIU_SK = os.environ.get('QINIU_SK')
    QINIU_BUCKET = os.environ.get('QINIU_BUCKET')

    @staticmethod
    def get_mailhandler():
        # email errors to the administrators
        from app.ext import MySMTPHandler
        credentials = None
        secure = None
        use_ssl = False
        if getattr(Config, 'MAIL_USERNAME', None) is not None:
            credentials = (Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            if getattr(Config, 'MAIL_USE_TLS', None):
                secure = ()
            use_ssl = getattr(Config, 'MAIL_USE_SSL', False)
        mail_handler = MySMTPHandler(
                mailhost=(Config.MAIL_SERVER, Config.MAIL_PORT),
                fromaddr=Config.APP_MAIL_SENDER,
                toaddrs=[Config.APP_ADMIN],
                subject=Config.APP_MAIL_SUBJECT_PREFIX + ' Application Error',
                credentials=credentials,
                secure=secure,
                use_ssl=use_ssl
        )
        mail_handler.setLevel(logging.ERROR)
        return mail_handler

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):

    DEBUG = True

    SQLALCHEMY_ECHO = True

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data_dev_sqlite.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)


class BAEConfig(Config):

    BAE_AK = ''
    BAE_SK = ''

    # BAE MEMCACHE
    CACHE_USER = BAE_AK
    CACHE_PWD = BAE_SK
    CACHE_ADDR = 'cache.duapp.com:20243'
    CACHE_ID = ''

    # mysql config
    MYSQL_USER = BAE_AK
    MYSQL_PASS = BAE_SK
    MYSQL_HOST = 'sqld.duapp.com'
    MYSQL_PORT = '4050'
    MYSQL_DB = ''

    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)

        def _create_logger(bufcount=256):
            _logger = logging.getLogger()
            _logger.setLevel(logging.DEBUG)
            from bae_log import handlers
            _handler = handlers.BaeLogHandler(
                    ak=app.config.get('BAE_AK'), 
                    sk=app.config.get('BAE_SK'), 
                    bufcount=bufcount,
            )
            return _handler
        _logger = _create_logger(1)
        app.logger.addHandler(_logger)


class SAEConfig(Config):

    try:
        # 如果是SAE环境，请把下面3行的注释去掉 
        from sae.const import (
            MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASS, MYSQL_DB
        )

        SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
            MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
        )
    except:
        pass

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)

        _handler = logging.StreamHandler()
        app.logger.addHandler(_handler)


class JAEConfig(Config):

    # mysql config
    MYSQL_USER = ''
    MYSQL_PASS = ''
    MYSQL_HOST = ''
    MYSQL_PORT = ''
    MYSQL_DB = ''

    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
        MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
    )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)

        # http://jae.jd.com/help/create_app.html?targ=94#a32
        # logfile path: /home/vcap/app/logs/jae.log
        # this logfile would be clean when app rebuild or restart
        _log_file = os.path.join(os.getenv('HOME'), 'logs/jae.log')
        file_handler = logging.FileHandler(_log_file)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                                      '%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)


class ProductionConfig(Config):

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data_sqlite.db')

    # mysql config
    MYSQL_USER = ''
    MYSQL_PASS = ''
    MYSQL_HOST = ''
    MYSQL_PORT = ''
    MYSQL_DB = ''

    if len(MYSQL_USER)>0 and len(MYSQL_PASS)>0 and len(MYSQL_HOST)>0 \
            and len(MYSQL_PORT)>0 and len(MYSQL_DB)>0:
        SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s:%s/%s' % (
            MYSQL_USER, MYSQL_PASS, MYSQL_HOST, MYSQL_PORT, MYSQL_DB
        )

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)


config = {
    'bae': BAEConfig,
    'default': DevelopmentConfig,
    'development': DevelopmentConfig,
    'jae': JAEConfig,
    'local': DevelopmentConfig,
    'production': ProductionConfig,
    'sae': SAEConfig,
}
