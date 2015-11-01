应用部署
========

基本要求: Python 2.7.X

运行环境
--------

APP的运行环境默认会根据服务器环境变量 ``SERVER_SOFTWARE`` 来确定.
BAE/JAE/SAE 这 3 个环境的 ``SERVER_SOFTWARE`` 是固定的;
其他环境可以通过设置机器的环境变量 ``APP_CONFIG`` 来更改默认的运行环境.

**LINUX设置方法（示例）** ::

    APP_CONFIG='production' python manage.py deploy

**WINDOWS设置方法（示例）** ::

    set APP_CONFIG=production
    python manage.py deploy

**运行环境说明:**

+-------------------------------+-------------------------------------------+
| ``development/default/local`` | 调试开发环境, 默认的选项, 使用内置服务器, |
|                               | 运行应用时为这个环境                      |
+-------------------------------+-------------------------------------------+
| ``production``                | 生产环境,                                 |
|                               | 一般是指通过 Gunicorn 运行应用时的环境    |
+-------------------------------+-------------------------------------------+
| ``testing``                   | 测试环境                                  |
+-------------------------------+-------------------------------------------+
| ``bae``                       | BAE应用引擎环境                           |
+-------------------------------+-------------------------------------------+
| ``jae``                       | JAE应用引擎环境                           |
+-------------------------------+-------------------------------------------+
| ``sae``                       | SAE应用引擎环境                           |
+-------------------------------+-------------------------------------------+


部署应用
--------

.. note::
   SQLAlchemy 数据库连接 URI 也可通过操作系统环境变量 ``DATABASE_URI`` 设置.

本地环境
++++++++

**本地环境** 是指对操作系统有绝对操作权的环境, 主要指 Windows 和 Linux 开发环境,
以及Linux生产环境.

本地环境通过 pip + virtualenv 方式部署.

**下载源码:**

从 https://github.com/wtx358/wtxlog/ 下载 wtxlog 最新源代码

**安装依赖:**

使用 ``requirements/common.txt`` 来安装依赖, 本地环境默认使用SQLite数据库::

    pip install -r requirements/common.txt

**运行程序:**

如果通过 virtualenv 来运行程序, 需要先激活虚拟环境.

初始化数据库::

    python manage.py deploy

运行程序::

    python manage.py runserver

若需要强制开启 debug 和 reload 的模式, 请加上参数 ``-d -r``.


BAE环境
+++++++

参考: :ref:`secret_key` , :ref:`database` , :ref:`cache`

**准备工作:**

1. 申请 BAE 账号, 创建工程, 解决方案勾选 **使用BAE**, 类型选择 **python-web**,
   代码版本工具建议选择 **Git**.
2. 进入 BAE3 应用管理控制台, 开发者服务 -> 应用引擎
3. 在 **扩展服务** 中添加 **BAE MySQL数据库**, 记下数据库相关信息, 后面会用到
4. 在 **扩展服务** 中添加 **Cache 服务** (如果有配额的话), 记下 **资源名称**
5. 在 **部署列表** 中 **添加部署**, 类型选择 **python-web**,
   使用 SVN 或 GIT 工具将代码 checkout 到本地

**更改设置:**

1. 从 https://github.com/wtx358/wtxlog/ 下载 wtxlog 最新源代码
2. 编辑根目录下的 ``config.py`` 文件

   更改 ``SECRET_KEY`` （位于 ``Config`` 类）::

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

   ``SECRET_KEY`` 可使用 ``os.urandom(24)`` 随机生成.

   更改 BAE 相关信息 （位于 ``BAEConfig`` 类）::

    BAE_AK = ''
    BAE_SK = ''

    # BAE MEMCACHE
    CACHE_TYPE = 'wtxlog.ext.baememcache'
    CACHE_BAE_USERNAME = BAE_AK
    CACHE_BAE_PASSWORD = BAE_SK
    CACHE_BAE_SERVERS = 'cache.duapp.com:20243'
    CACHE_BAE_ID = ''

    # mysql configuration
    MYSQL_USER = BAE_AK
    MYSQL_PASS = BAE_SK
    MYSQL_HOST = 'sqld.duapp.com'
    MYSQL_PORT = '4050'
    MYSQL_DB = ''

   若没有启用 Cache 服务或者方便调试, 请把 ``CACHE_TYPE`` 注释掉.

**设置依赖:**

修改根目录 ``requirements.txt`` 文件内容如下::

    -r requirements/bae3.txt

应用引擎会自动安装依赖.

**上传:**

1. 将前面修改好的 wtxlog 代码拷贝到 BAE 本地目录
2. 通过 SVN/GIT 上传所有文件
3. 上传之后发布到最新版本

接下来: :ref:`database_init` , :ref:`adminer`

SAE环境
+++++++

参考: :ref:`secret_key`, :ref:`cache`

**准备工作:**

1. 申请 SAE 开发账号, 创建 Python Web 应用

   SAE 新手入门: http://sae.sina.com.cn/doc/tutorial/index.html

2. 进入 SAE 应用管理控制台
3. 在服务管理中初始化 MySQL 数据库
4. 在服务管理中初始化 Memcache
5. 使用 SVN 工具将代码 checkout 到本地

**更改设置:**

1. 从 https://github.com/wtx358/wtxlog/ 下载 wtxlog 最新源代码
2. 修改应用信息, 编辑根目录下的 ``config.yaml`` 文件

   将 ``config.yaml`` 的 ``name`` 和 ``version`` 改为你自己的::

    name: appname
    version: 1

3. 更改设置, 编辑根目录下的 ``config.py`` 文件

   更改 ``SECRET_KEY`` (位于 ``Config`` 类)::

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

   ``SECRET_KEY`` 可使用 ``os.urandom(24)`` 随机生成.

   缓存设置(位于 ``SAEConfig`` 类), SAE 内置 Memcached 缓存服务,
   需要在控制面板初始化::

    CACHE_TYPE = 'memcached'

   若没有初始化 Memcached 服务或者方便调试, 请把 ``CACHE_TYPE`` 注释掉.

**安装依赖:**

SAE 预装有一些模块, 但有些版本比较旧, 且不支持通过 ``requirements.txt``
自动安装依赖, 所以只能把依赖包导出来, 连同代码一起上传到 SVN 代码库.

基本思路: 先本地通过 virtualenv 安装好依赖, 然后利用 ``bundle.py`` 导出依赖,
最后复制到应用根目录下的 ``mydeps`` 或者 ``deps`` 目录.

**步骤如下:**

(1) 使用 ``virtualenv`` 创建一个 pip 虚拟环境, 并进入:

    LINUX::

        virtualenv myenv
        source myenv/bin/activate

    WINDOWS::

        virtualenv myenv
        myenv\Scripts\activate.bat

(2) 把 ``requirements/common.txt`` 复制到当前目录, 并命名为 ``requirements.txt``

(3) 使用 ``requirements.txt`` 安装依赖包::

        pip install -r requirements.txt

(4) 使用 ``bundle_local.py`` 导出依赖包::

        python bundle_local.py -r requirements.txt

    PS: ``bundle_local.py`` 可在 https://github.com/sinacloud/sae-python-dev-guide 找到.

(5) 现在当前目录下会有一个 ``virtualenv.bundle`` 目录,
    把 ``virtualenv.bundle`` 目录下的所有内容复制到 ``mydeps`` 或者 ``deps`` 目录即可.

    虽然 SAE 支持 ``virtualenv.bundle.zip`` 这种依赖包导入方式, 但经过测试,
    会引发一些不可控的问题, 所以不建议使用这种方式.

**上传:**

1. 将前面修改好的 wtxlog 代码拷贝到 SAE 本地目录
2. 使用 SVN 上传所有文件
3. 代码上传后应用引擎会自动部署代码

接下来: :ref:`database_init`, :ref:`adminer`

JAE环境
+++++++

参考: :ref:`secret_key` , :ref:`database`

**准备工作**

1. 申请 JAE 开发账号, 新建应用, **应用服务器类型** 选择 **Python-Web**
2. 进入 JAE 应用引擎控制台
3. 在云数据库中新建 MySQL 数据库, 记下数据库相关信息, 后面会用到
4. 使用 GIT 工具将代码 clone 到本地


**更改设置:**

1. 从 https://github.com/wtx358/wtxlog/ 下载 wtxlog 最新源代码
2. 编辑根目录下的 ``config.py`` 文件

   更改 ``SECRET_KEY`` (位于 ``Config`` 类)::

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

   ``SECRET_KEY`` 可使用 ``os.urandom(24)`` 随机生成.

   更改 JAE 相关信息(位于 ``JAEConfig`` 类)::

    # mysql configuration
    MYSQL_USER = ''
    MYSQL_PASS = ''
    MYSQL_HOST = ''
    MYSQL_PORT = ''
    MYSQL_DB = ''

**设置依赖:**

修改根目录 ``requirements.txt`` 文件内容如下::

    -r requirements/jae.txt

应用引擎会自动安装依赖.

**上传:**

1. 将前面修改好的 wtxlog 代码拷贝到 BAE 本地目录
2. 通过 GIT 上传所有文件
3. 上传之后进行快速部署

   PS: 如果部署不成功, 多试几次, 或者加大内存再试.

接下来: :ref:`database_init`, :ref:`adminer`

生产环境
++++++++

推荐使用 Nginx + Gunicorn + Supervisor 这种相对简单的部署方式.

**安装 Supervisor:**

Supervisor 通过 easy_install 或 pip 在系统级别安装::

    easy_install supervisor

或者::

    pip install supervisor

**安装 Gunicorn:**

Gunicorn 通过 Virtualenv 在虚拟环境安装::

    pip install gunicorn==18.0

**安装依赖:**

安装 ``requirements/common.txt`` 中的依赖即可::

    pip install -r requirements/common.txt

**配置文件:**

注意: ``{{approot}}`` 为 wtxlog 应用程序实际所在绝对路径, 请替换为实际路径.

Supervisor 配置::

    [program:wtxlog]
    user=www
    directory={{approot}}
    command=/bin/env env/bin/gunicorn -b unix:app_wtxlog.sock manage:app
    process_name=%(program_name)s
    numprocs=1
    autostart=true
    autorestart=true
    stopsignal=QUIT
    redirect_stderr=true


Nginx 配置::

    server
    {
        server_name example.com;

        set $approot {{approot}};
        root $approot/wtxlog;

        location / { try_files $uri @myapp; }
        location @myapp {
            proxy_pass http://unix:$approot/app_wtxlog.sock;
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location ~ .*\.(gif|jpg|jpeg|png|bmp|swf)$
        {
            expires      30d;
        }

        location ~ .*\.(js|css)?$
        {
            expires      12h;
        }

        location ^~ /admin/static/ {
            alias $approot/wtxlog/static/admin/;
            expires 30d;
        }

        location ^~ /_themes/imtx/ {
            alias $approot/wtxlog/themes/imtx/static/;
            expires 10d;
        }

        access_log  /path/to/example.com.log  access;
    }


.. _database_init:

数据库初始化
++++++++++++

**方法1**

若拥有操作系统的操作权, 可通过下面的方法初始化::

    $ python manage.py deploy

**方法2**

在应用引擎中, 通过导入 ``schema.sql`` 文件的方法初始化数据库.


.. _adminer:

网站管理员
++++++++++

**方法1**

在 ``config.py`` 中设置好之后, 在网页上用对应的邮箱注册账号并激活即可.

**方法2**

先注册账号, 然后修改数据库相关记录, 然后修改下面两个字段的值:

* ``role_id`` 设置为 ``Administrator`` 对应的数值
* ``confirmed`` 设置为逻辑真(或者数值1)


配置信息
--------

内置的配置值
++++++++++++

.. list-table::

  * - THEME
    - 主题(模板)的名称
  * - SITE_NAME
    - 站点名称
  * - BLOG_MODE
    - 博客模式, 默认为 ``True``, 如果要做为 CMS, 则设为 ``False``
  * - BODY_FORMAT
    - 正文格式, 支持 MARKDOWN 和 HTML 两种
  * - SECRET_KEY
    - 密钥, 必须设置, 很重要
  * - MAIL_SERVER
    - 邮件服务器地址
  * - MAIL_PORT
    - 邮件服务器端口, 默认为25
  * - MAIL_USERNAME
    - 邮件服务器用户名, 注意是明文的
  * - MAIL_PASSWORD
    - 邮件服务器用户密码, 注意是明文的
  * - MAIL_USE_TLS
    - 使用 TLS 连接, GMAIL邮箱需要设置为 ``True``
  * - MAIL_USE_SSL
    - 使用 SSL 连接, QQ企业邮箱需要设置为 ``True``
  * - APP_ADMIN
    - 网站管理员邮箱
  * - CACHE_TYPE
    - 缓存类型, 有 ``simple``, ``memcached``, ``filesystem``,
      ``wtxlog.ext.baememcache`` 4 种.
  * - CACHE_KEY
    - 缓存名称, 默认值为 ``view/%s``
  * - CACHE_DEFAULT_TIMEOUT
    - 缓存过期时间, 默认为 300 秒
  * - CACHE_KEY_PREFIX
    - 内存类缓存前缀, 只对 RedisCache/MemcachedCache/GAEMemcachedCache 有效
  * - QINIU_AK
    - 七牛云存储 API Key
  * - QINIU_SK
    - 七牛云存储 Secret Key
  * - QINIU_BUCKET
    - 七牛云存储 bucket 名称
  * - QINIU_DOMAIN
    - 七牛云存储域名, 默认为 ``bucket.qiniudn.com``
  * - BAE_AK
    - BAE 应用引擎 API Key
  * - BAE_SK
    - BAE 应用引擎 Secret Key
  * - CACHE_BAE_SERVERS
    - BAE CACHE 服务主机地址
  * - CACHE_BAE_ID
    - BAE CACHE 服务名称
  * - CACHE_BAE_USERNAME
    - BAE CACHE 服务用户名, 默认与 ``BAE_AK`` 相同
  * - CACHE_BAE_PASSWORD
    - BAE CACHE 服务用户密码, 默认与 ``BAE_SK`` 相同
  * - MYSQL_HOST
    - MYSQL 主机地址
  * - MYSQL_PORT
    - MYSQL 主机端口
  * - MYSQL_USER
    - MYSQL 用户名
  * - MYSQL_PASS
    - MYSQL 用户密码
  * - MYSQL_DB
    - MYSQL 数据库名称

管理员邮箱及SMTP信息
++++++++++++++++++++++++

编辑 ``config.py``, 找到下面的内容(位于 ``Config`` 类), 并修改为自己对应的信息即可::

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

说明: 因为有些 SMTP 服务器强制要求发件地址与发件人一致(以防发送假冒邮件),
所以建议 ``MAIL_USERNAME`` 设置为完整邮件地址.

七牛云存储接口信息
++++++++++++++++++

编辑 ``config.py``, 找到下面的内容(位于 ``Config`` 类), 并修改为自己对应的信息即可::

    # QiNiu Cloud Storage
    QINIU_AK = os.environ.get('QINIU_AK')
    QINIU_SK = os.environ.get('QINIU_SK')
    QINIU_BUCKET = os.environ.get('QINIU_BUCKET')

说明: 虽然各个引用引擎都提供云存储功能, 但接口差别比较大, 为了方便和统一,
决定使用第三方云存储来存储上传的文件.

七牛云存储官网: http://www.qiniu.com/

静态文件映射
++++++++++++

默认情况下已经根据各平台对静态文件映射进行处理了, JAE 目前不支持静态映射.

特别说明: 如果新增加主题模板, 则需要在 ``app.conf`` 或 ``config.yaml`` 增加映射关系.

网站名称
++++++++++++

编辑 ``config.py``, 找到下面的内容(位于 ``Config`` 类), 并修改为自己对应的信息即可::

    SITE_NAME = u'wtxlog'

注意是 Unicode 类型的.

.. _secret_key:

SECRET_KEY
++++++++++

编辑 ``config.py``, 找到下面的内容(位于 ``Config`` 类), 并修改为自己对应的信息即可::

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'

小提示: 可以使用 ``os.urandom(24)`` 来生成随机字符串.

示例::

    SECRET_KEY = '6\xbbyVZ\xe7\xb5\x80\xff\xcf\xae`*\xf32\x82\xcf=\xf9\x97z\x01_'

.. _cache:

缓存Cache
+++++++++

应用程序引擎一般会支持 Memcached 缓存(或者兼容 Memcached),
云主机(VPS)可使用 Memcached 或者 FileSystemCache.

**SAE**

SAE不需要设置, 只需要在控制面板初始化 Memcached 即可.

若需要禁用缓存或者方便调试, 请设置 ``SAEConfig.CACHE_TYPE`` 的值.

**BAE**

若要使用缓存, 需要先在扩展服务里申请 **Cache 服务**, 并填写 Cache 相关信息.

编辑 ``config.py``, 找到下面的内容(位于 ``BAEConfig`` 类), 并修改为自己对应的信息即可::

    # BAE MEMCACHE
    CACHE_TYPE = 'wtxlog.ext.baememcache'
    CACHE_BAE_USERNAME = BAE_AK
    CACHE_BAE_PASSWORD = BAE_SK
    CACHE_BAE_SERVERS = 'cache.duapp.com:20243'
    CACHE_BAE_ID = ''


``BAE_AK``, ``BAE_SK`` 需要预先定义.

**JAE**

JAE 目前不支持 Memcached 缓存.

**云主机/VPS**

默认启用 Memcached 缓存.

若要启用 FileSystemCache, 编辑 ``config.py``,
找到下面的内容(位于 ``ProductionConfig`` 类), 把注释取消掉::

    # memcached type configuration values
    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']

    # filesystem type configuration values
    #CACHE_TYPE = 'filesystem'
    #CACHE_DIR = os.path.join(basedir, 'data', 'cache')


.. _database:

数据库配置
++++++++++

本地环境或者虚拟主机可以使用 SQLite 数据库, 但 BAE, SAE, JAE 目前只能使用 MySQL 数据库.

**BAE**

编辑 ``config.py``, 找到下面的内容(位于 ``BAEConfig`` 类中), 并修改为自己对应的信息即可::

    # mysql config
    MYSQL_USER = BAE_AK
    MYSQL_PASS = BAE_SK
    MYSQL_HOST = 'sqld.duapp.com'
    MYSQL_PORT = '4050'
    MYSQL_DB = ''

``BAE_AK``, ``BAE_SK`` 需要预先定义.

**SAE**

SAE 环境数据库信息可以通过应用引擎常量获取, 无需手动设置.

**JAE**

编辑 ``config.py``, 找到下面的内容(位于 ``JAEConfig`` 类中), 并修改为自己对应的信息即可::

    # mysql config
    MYSQL_USER = ''
    MYSQL_PASS = ''
    MYSQL_HOST = ''
    MYSQL_PORT = ''
    MYSQL_DB = ''

网站图标 favicon.ico
++++++++++++++++++++++++

``favicon.ico`` 默认路径为 ``wtxlog/static/favicon.ico``, 若有需要, 直接替换即可.
建议尺寸 16x16 或者 32x32.

