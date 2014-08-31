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
