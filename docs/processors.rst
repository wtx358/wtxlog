环境处理器
==========

本文介绍程序内置的一些环境处理器，可在模板文件中直接使用。

pager
-----

目前暂时弃用。

archives
--------

返回从第一篇文章开始到现在所经历的月份列表

category_lists
--------------

返回栏目列表。

参数：

- parent 父级栏目，默认为None
- limit 限制返回的数量，默认为None，即全部返回

category_tree
-------------

返回栏目树形列表。

tag_lists
---------

返回Tags标签列表

参数：

- limit 限制返回的数量

get_related_articles
--------------------

返回指定文章的相关文章列表。

参数：

- article_id 文章ID
- limit 限制返回的数量，默认为10

get_latest_articles
-------------------

返回最新文章列表。

参数：

- category 文章栏目，如果指定，则返回当前栏目（含子栏目）的最新文章，否则返回全局的
- limit 限制返回的数量，默认为10

get_top_articles
----------------

返回热门文章列表，根据hits降序。

参数：

- days 天数，比如显示一周热门，就可以设置为7，默认为365，即按年筛选
- limit 限制返回的数量，默认为10

get_recommend_articles
----------------------

返回推荐的文章列表。

参数：

- limit 限制返回的数量，默认为10

friendlinks
-----------

返回友情链接列表。

get_articles_by_tag
-------------------

根据Tag标签名称（name）返回文章列表。

参数：

- name 标签名称
- limit 限制返回的数量，默认为10

get_articles_by_category
------------------------

根据栏目返回文章列表。

参数：

- longslug 栏目的路径
- limit 限制返回的数量，默认为10
- showall 是否显示子栏目文章，默认为False

