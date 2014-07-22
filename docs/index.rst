.. wtxlog documentation master file, created by
   sphinx-quickstart on Tue Jul 22 22:43:55 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to wtxlog's documentation!
==================================

wtxlog是一个基于Python Flask的博客/CMS系统，力求简单。使用SQLAlchemy管理数据库，
支持SQLITE和MYSQL数据库，可轻松部署在各种云主机以及应用引擎（BAE/JAE/SAE等）上。

主要特性：

* 兼容性好，各种环境轻松部署
* 支持SQLITE和Mysql两种数据库
* 支持Memcached缓存
* 内置CKEditor富文本编辑器
* 使用Flask-Admin做为管理后台
* 后期会增加会员功能
* 可自定义模板主题
* 内置专题、栏目、标签、文章等常见模型

Contents:

.. toctree::
   :maxdepth: 2
   
   installation
   models
   filters
   processors

