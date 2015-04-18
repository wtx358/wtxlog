# -*- coding: utf-8 -*-

import logging
import datetime
from urllib2 import quote
from flask import current_app, request, redirect, url_for
from functools import wraps
from flask.ext.babelex import Babel
from flask.ext.cache import Cache as FlaskCache
from flask.ext.mail import Mail, Message
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from werkzeug._compat import text_type, to_bytes


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

    def get_subject(self, record):
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
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.mailhost, port, timeout=self._timeout)
            else:
                smtp = smtplib.SMTP(self.mailhost, port, timeout=self._timeout)

            _msg = self.format(record)
            msg = Message(self.get_subject(record),
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


class WtxlogCache(FlaskCache):

    def init_app(self, app, config=None):
        super(WtxlogCache, self).init_app(app)
        self.app = app

    def cached(self, timeout=None, key_prefix=None, unless=None):
        """
        Decorator. Use this to cache a function. By default the cache key
        is `view/request.path`. You are able to use this decorator with any
        function by changing the `key_prefix`. If the token `%s` is located
        within the `key_prefix` then it will replace that with `request.path`

        Example::

            # An example view function
            @cache.cached(timeout=50)
            def big_foo():
                return big_bar_calc()

            # An example misc function to cache.
            @cache.cached(key_prefix='MyCachedList')
            def get_list():
                return [random.randrange(0, 1) for i in range(50000)]

            my_list = get_list()

        .. note::

            You MUST have a request context to actually called any functions
            that are cached.

        .. versionadded:: 0.4
            The returned decorated function now has three function attributes
            assigned to it. These attributes are readable/writable.

                **uncached**
                    The original undecorated function

                **cache_timeout**
                    The cache timeout value for this function. For a custom value
                    to take affect, this must be set before the function is called.

                **make_cache_key**
                    A function used in generating the cache_key used.

        :param timeout: Default None. If set to an integer, will cache for that
                        amount of time. Unit of time is in seconds.
        :param key_prefix: Default 'view/%(request.path)s'. Beginning key to .
                           use for the cache key.

                           .. versionadded:: 0.3.4
                               Can optionally be a callable which takes no arguments
                               but returns a string that will be used as the cache_key.

        :param unless: Default None. Cache will *always* execute the caching
                       facilities unless this callable is true.
                       This will bypass the caching entirely.
        """
        if key_prefix is None:
            key_prefix = self.app.config.get('CACHE_KEY', 'view/%s')
        if timeout is None:
            timeout = self.app.config.get('CACHE_DEFAULT_TIMEOUT', 300)

        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # 如果是第一页，跳转到标准页面
                # 比如： `/page/1/` 跳转到 `/`
                _kw = request.view_args
                if 'page' in _kw and _kw['page'] == 1:
                    _kw.pop('page')
                    return redirect(url_for(request.endpoint, **_kw), code=301)

                # Bypass the cache entirely.
                if callable(unless) and unless() is True:
                    return f(*args, **kwargs)

                try:
                    cache_key = decorated_function.make_cache_key(*args, **kwargs)
                    if request.MOBILE:
                        cache_key = 'mobile_%s' % cache_key
                    rv = self.cache.get(cache_key)
                except Exception:
                    if current_app.debug:
                        raise
                    current_app.logger.exception("Exception possibly due to cache backend.")
                    return f(*args, **kwargs)

                if rv is None:
                    rv = f(*args, **kwargs)

                    # 添加缓存时间信息
                    _suffix = u"\n<!-- cached at %s -->" % str(datetime.datetime.now())
                    if hasattr(rv, "data"):
                        rv.data = '%s%s' % (rv.data, _suffix)
                    if isinstance(rv, text_type):
                        rv = '%s%s' % (rv, _suffix)

                    try:
                        self.cache.set(cache_key, rv, decorated_function.cache_timeout)
                    except Exception:
                        if current_app.debug:
                            raise
                        current_app.logger.exception("Exception possibly due to cache backend.")
                        return f(*args, **kwargs)
                return rv

            def make_cache_key(*args, **kwargs):
                if callable(key_prefix):
                    cache_key = key_prefix()
                elif '%s' in key_prefix:
                    # 这里要转换成str(UTF-8)类型, 否则会报类型错误
                    _path = to_bytes(request.path, 'utf-8')
                    # 对于非ASCII的URL，需要进行URL编码
                    if quote(_path).count('%25') <= 0:
                        _path = quote(_path)
                    cache_key = key_prefix % _path
                else:
                    cache_key = key_prefix

                return cache_key

            decorated_function.uncached = f
            decorated_function.cache_timeout = timeout
            decorated_function.make_cache_key = make_cache_key

            return decorated_function
        return decorator


def baememcache(app, config, args, kwargs):
    from bae_memcache import BaeMemcache
    return BaeMemcache(config['CACHE_BAE_ID'],
                       config['CACHE_BAE_SERVERS'],
                       config['CACHE_BAE_USERNAME'],
                       config['CACHE_BAE_PASSWORD'])


mail = Mail()
db = SQLAlchemy()
babel = Babel()

login_manager = LoginManager()
cache = WtxlogCache()


@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'zh_CN', 'zh_TW'])
