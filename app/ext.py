# -*- coding: utf-8 -*-

import logging
import datetime
from urllib2 import quote, unquote
from flask import current_app, request
from functools import wraps
from flask.ext.mail import Mail, Message
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from werkzeug.contrib.cache import NullCache, SimpleCache


def keywords_split(keywords):
    return keywords.replace(u',', ' ') \
                   .replace(u';', ' ') \
                   .replace(u'+', ' ') \
                   .replace(u'；', ' ') \
                   .replace(u'，', ' ') \
                   .replace(u'　', ' ') \
                   .split(' ')


class MySMTPHandler(logging.Handler):
    """
    A handler class which sends an SMTP email for each logging event.

    默认不支持SSL协议的，增加参数use_ssl，如果使用SSL，则使用SMTP_SSL
    """
    def __init__(self, mailhost, fromaddr, toaddrs, subject,
                 credentials=None, secure=None, use_ssl=False):
        """
        Initialize the handler.

        Initialize the instance with the from and to addresses and subject
        line of the email. To specify a non-standard SMTP port, use the
        (host, port) tuple format for the mailhost argument. To specify
        authentication credentials, supply a (username, password) tuple
        for the credentials argument. To specify the use of a secure
        protocol (TLS), pass in a tuple for the secure argument. This will
        only be used when authentication credentials are supplied. The tuple
        will be either an empty tuple, or a single-value tuple with the name
        of a keyfile, or a 2-value tuple with the names of the keyfile and
        certificate file. (This tuple is passed to the `starttls` method).
        """
        logging.Handler.__init__(self)
        if isinstance(mailhost, tuple):
            self.mailhost, self.mailport = mailhost
        else:
            self.mailhost, self.mailport = mailhost, None
        if isinstance(credentials, tuple):
            self.username, self.password = credentials
        else:
            self.username = None
        self.fromaddr = fromaddr
        if isinstance(toaddrs, basestring):
            toaddrs = [toaddrs]
        self.toaddrs = toaddrs
        self.subject = subject
        self.secure = secure
        self.use_ssl = use_ssl
        self._timeout = 5.0

    def getSubject(self, record):
        """
        Determine the subject for the email.

        If you want to specify a subject line which is record-dependent,
        override this method.
        """
        return self.subject

    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            from email.utils import formatdate
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self._timeout)
            else:
                smtp = smtplib.SMTP(self.mailhost, port, timeout=self._timeout)

            _msg = self.format(record)
            msg = Message(self.getSubject(record),
                          sender=self.fromaddr, recipients=self.toaddrs)
            msg.body = _msg

            if self.username:
                if self.secure is not None:
                    smtp.ehlo()
                    smtp.starttls(*self.secure)
                    smtp.ehlo()
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg.as_string())
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


class Cache(object):
    '''cache object'''
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        config = app.config.copy()
        appenv = config.get('APPENV')
        (_k, _v) = ('key31415926', '3.1415926')

        if config['DEBUG']:
            _cache = NullCache()
        else:
            if appenv == 'bae':
                from bae_memcache.cache import BaeMemcache
                CACHE_USER = config.get('CACHE_USER')
                CACHE_PWD = config.get('CACHE_PWD')
                CACHE_ID = config.get('CACHE_ID')
                CACHE_ADDR = config.get('CACHE_ADDR')
                _cache = BaeMemcache(CACHE_ID, CACHE_ADDR, CACHE_USER, CACHE_PWD)
                try:
                    _cache.set(_k, _v)
                except:
                    _cache = NullCache()
            elif appenv == 'sae':
                import pylibmc as memcache
                _cache = memcache.Client()
                try:
                    _cache.set(_k, _v)
                except:
                    _cache = NullCache()
            elif appenv == 'production':
                _cache = SimpleCache()
                try:
                    import memcache
                    _mc = memcache.Client(app.config.get('MEMCACHED_SERVERS', []))
                    if _mc.set(_k, _v):
                        _cache = _mc
                except:
                    pass
            else:
                _cache = NullCache()

        app.extensions['cache'] = _cache

    @property
    def cache(self):
        app = self.app or current_app
        return app.extensions['cache']

    def cached(self, timeout=60 * 60, key=None):
        cache = self.cache
        if key is None:
            key = self.app.config['MEMCACHE_KEY']

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                page = int(request.args.get('page', 1))

                # 这里要转换成str类型, 否则会报类型错误
                _path = request.path.encode("utf-8")

                # 对于非ASCII的URL，需要进行URL编码
                if quote(_path).count('%25') <= 0:
                    _path = quote(_path)

                _viewkey = 'mobile%s' % _path if request.MOBILE else _path
                cache_key = str(key % _viewkey)

                if page > 1:
                    cache_key = '%s_%s' % (cache_key, page)

                rv = cache.get(cache_key)
                if rv is not None: 
                    return rv
                rv = f(*args, **kwargs)
                _suffix = u"\n<!-- cached at %s -->" % str(datetime.datetime.now())
                if hasattr(rv, "data"):
                    rv.data += _suffix
                if isinstance(rv, unicode):
                    rv += _suffix
                cache.set(cache_key, rv, timeout)
                return rv
            return decorated_function
        return decorator


mail = Mail()
db = SQLAlchemy()

login_manager = LoginManager()
cache = Cache()
