部署
====

基本要求： Python 2.7.X

设置依赖
--------

本地环境
++++++++

**本地环境** 是指对操作系统有绝对操作权的环境，主要指Windows和Linux开发环境，
以及Linux生产环境。

使用 ``requirements/common.txt`` 来安装依赖，本地环境默认使用SQLITE数据库::

    pip install -r requirements/common.txt

BAE环境
+++++++

只需要把 ``requirements.txt`` 的内容改成下面的即可，应用引擎会自动安装依赖::

    -r requirements/bae3.txt

SAE环境
+++++++

这个稍微有点复杂，需要在本地先安装好依赖，然后导出依赖，复制到 ``mydeps`` 
或者 ``deps`` 目录。

方法如下：

(1) 使用 ``virtualenv`` 创建一个pip虚拟环境，并进入

(2) 把 ``requirements/common.txt`` 复制到当前目录，并命名为 ``requirements.txt``

(3) 使用 ``requirements.txt`` 安装依赖包::

        pip install -r requirements.txt

(4) 使用 ``bundle_local.py`` 导出依赖包::

        python bundle_local.py -r requirements.txt

    PS: ``bundle_local.py`` 可在 https://github.com/sinacloud/sae-python-dev-guide 找到。

(5) 现在当前目录下会有一个 ``virtualenv.bundle`` 目录，把
    ``virtualenv.bundle`` 目录下的所有内容复制到 ``mydeps`` 或者 ``deps`` 目
    录即可。

    虽然 SAE 支持 ``virtualenv.bundle.zip`` 这种依赖包导入方式，但经过测
    试，会引发一些不可控的问题，所以不建议使用这种方式。

JAE环境
+++++++

只需要把 ``requirements.txt`` 的内容改成下面的即可，应用引擎会自动安装依赖::

    -r requirements/jae.txt


部署应用
--------

在BAE部署应用
+++++++++++++

通过SVN/GIT上传源代码上传之后，在控制面板手动部署。

上传前需要配置的地方： :ref:`secret_key` , :ref:`database` , :ref:`cache`

在SAE部署应用
+++++++++++++

通过SVN上传代码，代码上传之后自动部署。

上传前需要配置的地方： :ref:`secret_key` , :ref:`cache`

在JAE部署应用
+++++++++++++

通过GIT上传代码之后，在控制面板手动部署。

上传前需要配置的地方： :ref:`secret_key` , :ref:`database`

PS：由于PIP源的问题，经常会部署不成功，需要多试几次。

在Linux云主机（VPS）部署应用
++++++++++++++++++++++++++++

推荐使用 Nginx + Gunicorn + Supervisor 这种相对简单的部署方式。

数据库初始化
++++++++++++

**方法1**

若拥有操作系统的操作权，可通过下面的方法初始化::

    $ python manage.py deploy

**方法2**

在应用引擎中，通过导入 ``schema.sql`` 文件的方法初始化数据库。

网站管理员
++++++++++

**方法1**

在 ``config.py`` 中设置好之后，在网页上用对应的邮箱注册账号并激活即可。

**方法2**

先注册账号，然后修改数据库相关记录，然后修改下面两个字段的值：

* ``role_id`` 设置为 ``Administrator`` 对应的数值
* ``confirmed`` 设置为逻辑真（或者数值1）。


配置信息
--------

管理员邮箱及SMTP信息
++++++++++++++++++++++++

编辑 ``config.py`` ，找到下面的内容（位于 ``Config`` 类），并修改为自己对应的信息即可::

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    #MAIL_USE_TLS = True

    APP_MAIL_SUBJECT_PREFIX = '[%s]' % SITE_NAME
    APP_MAIL_SENDER = '%s Admin <%s>' % (SITE_NAME, MAIL_USERNAME)
    APP_ADMIN = os.environ.get('APP_ADMIN')

示例::

    MAIL_SERVER = 'smtp.126.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USERNAME = 'test01@126.com'
    MAIL_PASSWORD = 'yourpassword'
    #MAIL_USE_TLS = True

    APP_MAIL_SUBJECT_PREFIX = '[%s]' % SITE_NAME
    APP_MAIL_SENDER = '%s Admin <%s>' % (SITE_NAME, MAIL_USERNAME)
    APP_ADMIN = 'myadmin@126.com'

说明：因为有些SMTP服务器强制要求发件地址与发件人一致（以防发送假冒邮件），
所以建议 ``MAIL_USERNAME`` 设置为完整邮件地址。

七牛云存储接口信息
++++++++++++++++++

编辑 ``config.py`` ，找到下面的内容（位于 ``Config`` 类），并修改为自己对应的信息即可::

    # QiNiu Cloud Storage
    QINIU_AK = os.environ.get('QINIU_AK')
    QINIU_SK = os.environ.get('QINIU_SK')
    QINIU_BUCKET = os.environ.get('QINIU_BUCKET')

说明：虽然各个引用引擎都提供云存储功能，但接口差别比较大，为了方便和统一
，决定使用第三方云存储来存储上传的文件。

七牛云存储官网： http://www.qiniu.com/

静态文件映射
++++++++++++

默认情况下已经根据各平台对静态文件映射进行处理了，JAE目前不支持静态映射。

特别说明：如果新增加主题模板，则需要在 ``app.conf`` 或 ``config.yaml`` 增加映射关系。

网站名称
++++++++++++

编辑 ``config.py`` ，找到下面的内容（位于 ``Config`` 类），并修改为自己对应的信息即可::

    SITE_NAME = u'wtxlog'

注意是 Unicode 编码的。

.. _secret_key:

SECRET_KEY
++++++++++

编辑 ``config.py`` ，找到下面的内容（位于 ``Config`` 类），并修改为自己对应的信息即可::

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

小提示：可以使用 ``os.urandom(24)`` 来生成随机字符串。

示例::

    SECRET_KEY = '6\xbbyVZ\xe7\xb5\x80\xff\xcf\xae`*\xf32\x82\xcf=\xf9\x97z\x01_'

.. _cache:

缓存Cache
+++++++++

应用程序引擎一般会支持Memcached缓存（或者兼容Memcached），云主机（VPS）
可使用Memcached或者FileSystemCache。

SAE
~~~

SAE不需要设置，只需要在控制面板初始化Memcached即可。

若需要禁用缓存或者方便调试，请设置 ``SAEConfig.CACHE_TYPE`` 的值。

BAE
~~~

若要使用缓存，需要先在扩展服务里申请Cache服务，并填写Cache相关信息。

编辑 ``config.py`` ，找到下面的内容（位于 ``BAEConfig`` 类），并修改为自己对应的信息即可::

    # BAE MEMCACHE
    CACHE_TYPE = 'wtxlog.ext.baememcache'
    CACHE_BAE_USERNAME = BAE_AK
    CACHE_BAE_PASSWORD = BAE_SK
    CACHE_BAE_SERVERS = 'cache.duapp.com:20243'
    CACHE_BAE_ID = ''


``BAE_AK`` ,  ``BAE_SK`` 需要预先定义。

JAE
~~~

JAE目前不支持Memcached缓存。

云主机（VPS）
~~~~~~~~~~~~~

默认启用Memcached缓存。

若要启用FileSystemCache，编辑 ``config.py`` ，找到下面的内容
（位于 ``ProductionConfig`` 类），把注释取消掉::

    # memcached type configuration values
    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']

    # filesystem type configuration values
    #CACHE_TYPE = 'filesystem'
    #CACHE_DIR = os.path.join(basedir, 'data', 'cache')


.. _database:

数据库配置
++++++++++

本地环境或者虚拟机可以使用SQLITE数据库，但BAE,SAE,JAE目前只能使用MySQL数据库。

BAE
~~~

编辑 ``config.py`` ，找到下面的内容（位于 ``BAEConfig`` 类中），并修改为自己对应的信息即可::

    # mysql config
    MYSQL_USER = BAE_AK
    MYSQL_PASS = BAE_SK
    MYSQL_HOST = 'sqld.duapp.com'
    MYSQL_PORT = '4050'
    MYSQL_DB = ''

``BAE_AK`` ,  ``BAE_SK`` 需要预先定义。

SAE
~~~

SAE环境数据库信息可以通过应用引擎常量获取，无需手动设置。

JAE
~~~

编辑 ``config.py`` ，找到下面的内容（位于 ``JAEConfig`` 类中），并修改为自己对应的信息即可::

    # mysql config
    MYSQL_USER = ''
    MYSQL_PASS = ''
    MYSQL_HOST = ''
    MYSQL_PORT = ''
    MYSQL_DB = ''

网站图标 favicon.ico
++++++++++++++++++++++++

``favicon.ico`` 默认路径为 ``wtxlog/static/favicon.ico`` ，若有需要，直接替换即可。
建议尺寸16x16或者32x32。

