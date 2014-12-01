# -*- coding: utf-8 -*-

import os
import logging
from hashlib import md5

basedir = os.path.abspath(os.path.dirname(__file__))
datadir = 'data'


class Config:

    THEME = 'imtx'
    SITE_NAME = u'wtxlog'

    # 是否启用博客模式
    BLOG_MODE = True

    # html or markdown
    BODY_FORMAT = 'html'

    # tip: generate `SECRET_KEY` by `os.urandom(24)`
    SECRET_KEY = os.getenv('SECRET_KEY') or 'hard to guess string'

    # Consider SQLALCHEMY_COMMIT_ON_TEARDOWN harmful
    # SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    SQLALCHEMY_POOL_RECYCLE = 10

    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

    MAIL_SERVER = os.getenv('MAIL_SERVER') or ''
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or ''
    # gmail的话带下面那行的注释去掉
    # MAIL_USE_TLS = True
    # qq企业邮箱的话带下面那行的注释去掉
    # MAIL_USE_SSL = True

    APP_MAIL_SUBJECT_PREFIX = '[%s]' % SITE_NAME
    APP_MAIL_SENDER = '%s Admin <%s>' % (SITE_NAME, MAIL_USERNAME)
    APP_ADMIN = os.getenv('APP_ADMIN')

    # flask-cache basic configuration values
    CACHE_KEY = 'view/%s'
    CACHE_DEFAULT_TIMEOUT = 300

    # Used only for RedisCache, MemcachedCache and GAEMemcachedCache
    CACHE_KEY_PREFIX = '%s_' % md5(SECRET_KEY).hexdigest()[7:15]

    # QiNiu Cloud Storage
    QINIU_AK = os.getenv('QINIU_AK') or ''
    QINIU_SK = os.getenv('QINIU_SK') or ''
    QINIU_BUCKET = os.getenv('QINIU_BUCKET') or ''
    QINIU_DOMAIN = os.getenv('QINIU_DOMAIN') or '%s.qiniudn.com' % QINIU_BUCKET

    @staticmethod
    def get_mailhandler():
        # send email to the administrators if errors occurred
        from wtxlog.ext import MySMTPHandler
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

    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data_dev_sqlite.db')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        mail_handler = Config.get_mailhandler()
        app.logger.addHandler(mail_handler)


class TestingConfig(Config):

    TESTING = True

    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

    WTF_CSRF_ENABLED = False


class BAEConfig(Config):

    BAE_AK = os.getenv('BAE_AK') or ''
    BAE_SK = os.getenv('BAE_SK') or ''

    # BAE MEMCACHE
    CACHE_TYPE = 'wtxlog.ext.baememcache'
    CACHE_BAE_USERNAME = BAE_AK
    CACHE_BAE_PASSWORD = BAE_SK
    CACHE_BAE_SERVERS = os.getenv('CACHE_BAE_SERVERS') or 'cache.duapp.com:20243'
    CACHE_BAE_ID = os.getenv('CACHE_BAE_ID') or ''

    # mysql configuration
    MYSQL_USER = os.getenv('MYSQL_USER') or BAE_AK
    MYSQL_PASS = os.getenv('MYSQL_PASS') or BAE_SK
    MYSQL_HOST = os.getenv('MYSQL_HOST') or 'sqld.duapp.com'
    MYSQL_PORT = os.getenv('MYSQL_PORT') or '4050'
    MYSQL_DB = os.getenv('MYSQL_DB') or ''

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

    # 需要先在控制面板启用Memcached服务，否则会报错
    # 调试阶段，可以注释掉，或者改为其它类型，比如 simple
    CACHE_TYPE = 'memcached'

    try:
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

    CACHE_TYPE = 'simple'

    # mysql configuration
    MYSQL_USER = os.getenv('MYSQL_USER') or ''
    MYSQL_PASS = os.getenv('MYSQL_PASS') or ''
    MYSQL_HOST = os.getenv('MYSQL_HOST') or ''
    MYSQL_PORT = os.getenv('MYSQL_PORT') or ''
    MYSQL_DB = os.getenv('MYSQL_DB') or ''

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
        if os.path.isfile(_log_file):
            file_handler = logging.FileHandler(_log_file)
            formatter = logging.Formatter(
                '%(asctime)s %(levelname)-8s %(message)s',
                '%Y-%m-%d %H:%M:%S',
            )
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)


class ProductionConfig(Config):

    # memcached type configuration values
    # CACHE_TYPE = 'memcached'
    # CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']

    # filesystem type configuration values
    CACHE_TYPE = 'filesystem'
    CACHE_DIR = os.path.join(basedir, datadir, 'cache')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data_sqlite.db')

    # mysql configuration
    MYSQL_USER = os.getenv('MYSQL_USER') or ''
    MYSQL_PASS = os.getenv('MYSQL_PASS') or ''
    MYSQL_HOST = os.getenv('MYSQL_HOST') or ''
    MYSQL_PORT = os.getenv('MYSQL_PORT') or ''
    MYSQL_DB = os.getenv('MYSQL_DB') or ''

    if (len(MYSQL_USER) > 0 and len(MYSQL_PASS) > 0 and
            len(MYSQL_HOST) > 0 and len(MYSQL_PORT) > 0 and
            len(MYSQL_DB) > 0):
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
            'mysql://%s:%s@%s:%s/%s' % (MYSQL_USER, MYSQL_PASS, MYSQL_HOST,
                                        MYSQL_PORT, MYSQL_DB)

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
    'testing': TestingConfig,
    'sae': SAEConfig,
}
