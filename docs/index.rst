.. wtxlog documentation master file, created by
   sphinx-quickstart on Tue Jul 22 22:43:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

wtxlog (Flask BLOG/CMS)
=======================

Wtxlog 是基于 Python Flask 框架开发的开源的 BLOG/CMS 系统, 以 **简单实用** 为目标.
Wtxlog 内置栏目、标签(Tags)、文章等主要模型, 可以满足绝大部分的内容输出需求.
程序通用性良好, 各种云主机、VPS以及应用程序引擎(BAE/JAE/SAE等)均可轻松部署.

主要特性
--------

* **内置模型:** 栏目、标签、文章、专题、友情链接等
* **数据库:** 使用 SQLAlchemy 驱动, 主要支持 SQLite 和 Mysql 两种数据库
* **缓存功能:** 主要支持 Memcached 和 FileSystemCache 两种缓存方式
* **编辑器:** CKEditor 富文本编辑器, Markdown 编辑器, 内置图片上传功能
* **后台管理:** 使用 Flask-Admin 管理后台, 功能强大, 简单易用
* **换肤功能:** 可自定义皮肤(主题), 语法兼容 Jinja2.
  内置实用的过滤器和上下文处理器, 可实现常用的查询功能.
  模板设计符合 SEO 优化理念
* **静态标签:** 后台增加的HTML代码片断(静态标签), 可在模板文件中直接调用
* 支持通过 MetaWeblog 发布文章
* 新增文章发布后自动 Ping 通知百度
* 其它功能: Sitemap, Feed, robots.txt, favicon.ico, etc.

.. note::
   源码: `wtxlog @ GitHub <https://github.com/wtx358/wtxlog>`_

主要依赖的 Flask 扩展插件
-------------------------

* Flask-SQLAlchemy 数据库模型
* Flask-Cache 缓存
* Flask-Admin 后台管理
* Flask-Login 用户登录
* Flask-Mail 邮件发送


**Contents:**

.. toctree::
   :numbered:
   :maxdepth: 2

   installation.rst
   models.rst
   templating.rst

