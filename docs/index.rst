.. wtxlog documentation master file, created by
   sphinx-quickstart on Tue Jul 22 22:43:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

wtxlog (Flask BLOG/CMS)
=======================

Wtxlog是基于Python Flask开发的开源的BLOG/CMS系统，以“简单实用”为目标。
Wtxlog内置栏目、标签（Tags）、文章等主要模型，可以满足绝大部分的内容输出
需求。程序通用性良好，各种云主机、VPS以及应用程序引擎（BAE/JAE/SAE等）均
可轻松部署。

主要特性
--------

- 内置模型：栏目、标签、文章、专题、友情链接等
- 数据库：使用SQLAlchemy驱动，主要支持SQLITE和Mysql两种数据库
- 缓存功能：主要支持Memcached和FileSystemCache两种缓存方式
- 编辑器：CKEditor富文本编辑器，Markdown编辑器，带图片上传功能
- 后台管理：使用Flask-Admin管理后台，功能强大，简单易用
- 换肤功能：可自定义皮肤（主题），语法兼容Jinja2。内置实用的过滤器和上下
  文处理器，可实现常用的查询功能。模板设计符合SEO优化理念
- 代码片断：后台增加的代码片断，可在模板文件中直接调用
- 支持MetaWeblog发布文章
- 新增文章发布后自动PING通知百度
- 其它功能：Sitemap, Feed, robots.txt, favicon.ico, etc.

主要依赖的第三方Flask插件
-------------------------

- Flask-SQLAlchemy
- Flask-Cache
- Flask-Admin
- Flask-Login
- Flask-Mail


Contents:

.. toctree::
   :numbered:
   :maxdepth: 2

   installation.rst
   models.rst
   templating.rst

