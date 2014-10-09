============
主题（皮肤）
============

Wtxlog 支持主题切换功能（换肤功能），可以准备多套主题，只需简单设置就可
以轻松切换。

**主题** 也可以理解为“皮肤”。

主题
=====

Wtxlog使用flask-themes作为主题管理工具。主题目录下包含若干模板文件。

文件结构
--------

模板
====

模板语法与 Jinja2 相同。

过滤器
======

Jinja2所有内置的过滤器都是可以使用的。 本文介绍的是定制的一些过滤器：

markdown
--------

用Markdown语法处理文本。

参数：

- ``codehilite`` : 是否高亮代码，默认为 ``True``

date
----

日期格式化，格式化选项与Python标准相同。

timestamp
---------

时间戳格式化，格式化选项与Python标准相同。

emphasis
--------

强调关键词，即给文本中出现的关键词加上 ``em`` 标签。

主要用于搜索时高亮显示搜索词。

参数：

- ``keyword`` : 要强调的关键词

上下文处理器
============

本文介绍程序内置的一些 **上下文处理器** ，可在模板文件中直接使用。

**上下文处理器** 在模板渲染之前运行，并且可以在模板上下文中插入新值。

archives
--------

返回从第一篇文章开始到现在所经历的月份列表

category_lists
--------------

返回栏目列表。

参数：

- ``parent`` 父级栏目，默认为 ``None``
- ``limit`` 限制返回的数量，默认为 ``None`` ，即全部返回

tag_lists
---------

返回Tags标签列表

参数：

- ``limit`` 限制返回的数量

topic_lists
-----------

返回专题列表

参数：

- ``limit`` 限制返回的数量

category_tree
-------------

返回栏目树形列表。

get_related_articles
--------------------

返回指定文章的相关文章列表。

参数：

- ``article_id`` 文章ID
- ``limit`` 限制返回的数量，默认为10

get_latest_articles
-------------------

返回最新文章列表。

参数：

- ``category`` 文章栏目，如果指定，则返回当前栏目（含子栏目）的最新文章，否则返回全局的
- ``limit`` 限制返回的数量，默认为10

get_top_articles
----------------

返回热门文章列表，根据hits降序。

参数：

- ``days`` 天数，比如显示一周热门，就可以设置为7，默认为365，即按年筛选
- ``limit`` 限制返回的数量，默认为10

get_recommend_articles
----------------------

返回推荐的文章列表。

参数：

- ``category`` 文章栏目，如果指定，则返回当前栏目（含子栏目）的最新文章，否则返回全局的
- ``limit`` 限制返回的数量，默认为10

get_thumbnail_articles
----------------------

返回有缩略图的文章列表。

参数：

- ``category`` 文章栏目，如果指定，则返回当前栏目（含子栏目）的最新文章，否则返回全局的
- ``limit`` 限制返回的数量，默认为10

get_articles_by_category
------------------------

根据栏目路径（longslug）返回文章列表。

参数：

- ``longslug`` 栏目路径，字符串，不要以 ``/`` 结尾
- ``limit`` 返回的个数，整数
- ``expand`` 是否返回子栏目文章， 若为 ``False`` 则只返回当前栏目的文章

friendlinks
-----------

返回友情链接列表。

label
-----

返回静态标签的内容

参数：

- ``slug`` 标签的英文标识符，unicode类型

示例 ::

    {{ label('index_title') }}

model_query
-----------

模型复杂查询

参数：

- ``model`` 实例模型，比如 ``Article`` , ``Category`` , ``Tag`` , etc.
- ``search_params`` 参数字典，为dict类型，参照 `flask-restless文档 <http://flask-restless.readthedocs.org/en/latest/>`_

示例 ::

    {% set longslug = '' %}
    {% if article %}{% set longslug = article.category.longslug %}{% endif %}
    {% if category %}{% set longslug = category.longslug %}{% endif %}
    {% with recent_articles = model_query(Article,
    {'order_by': [{'field': 'id', 'direction': 'desc'}],
     'limit': 15,
     'filters': [
      {'name': 'category_id', 'op': 'in', 'val': get_category_ids(longslug)},
      {'name': 'published', 'op': 'eq', 'val': True}],
    }) %}
    {% for article in recent_articles -%}
    <li><a href="{{ article.link }}">{{ article.title }}</a></li>
    {% endfor %}
    {% endwith %}

因为这个方法使用相当复杂（参数看起来比较多，语法略为复杂），所以只有当上
面列举的上下文处理器无法实现某个查询功能时，才建议使用这个方法来实现。
