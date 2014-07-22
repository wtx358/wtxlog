模型
====

栏目 Category
-------------

**基本属性：**

- id
- slug 英文标识符
- longslug 栏目路径
- name 栏目名称
- parent 父级栏目
- seotitle SEO标题
- seokey SEO关键词
- seodesc SEO描述
- thumbnail 缩略图URL
- template 栏目页模板文件
- article_template 栏目下属文章页模板文件
- body 栏目介绍（正常情况下是MARKDOWN格式）
- body_html 栏目介绍HTML

**特殊属性：**

- link 栏目的URL链接（带域名）
- shortlink 栏目的URL链接
- count 栏目文章数（包含子栏目）
- parents 栏目的上级目录列表
- tree 树形列表

标签 Tag
--------

**基本属性：**

- id
- name Tag名称
- seotitle SEO标题
- seokey SEO关键词
- seodesc SEO描述
- thumbnail 缩略图URL
- template Tag列表页模板文件
- body Tag介绍（正常情况下是MARKDOWN格式）
- body_html Tag介绍HTML

**特殊属性：**

- link Tag的URL链接（带域名）
- shortlink Tag的URL链接
- count Tag文章数

专题 Topic
----------

**基本属性：**

- id
- slug 英文唯一标识符
- name 专题名称
- seotitle SEO标题
- seokey SEO关键词
- seodesc SEO描述
- thumbnail 缩略图URL
- template 专题页模板文件
- body 专题介绍（正常情况下是MARKDOWN格式）
- body_html 专题介绍HTML

**特殊属性：**

- link Tag的URL链接（带域名）
- shortlink Tag的URL链接
- count Tag文章数

文章 Article
------------

**基本属性：**

- id
- slug 英文标识符，目前暂时无效
- title 文章标题
- seotitle SEO标题
- seokey SEO关键词
- seodesc SEO描述
- category 文章所属栏目（必选）（基于Category模型）
- topic 文章所属专题（可选）（基于Topic模型）
- tags 文章Tags标签列表（基于Tag模型）
- thumbnail 缩略图URL
- thumbnail_big 大缩略图URL
- template 文章内容页模板文件
- summary 文章摘要
- body 文章正文（正常情况下是MARKDOWN格式）
- body_html 文章正文HTML
- published 是否发布
- ontop 是否置顶
- recommend 是否推荐
- hits 点击数
- author 文章作者（基于User模型）
- created 文章创建的时间
- last_modified 最后更新的时间

**特殊属性：**

- has_more 是否有MORE分隔符
- link 文章的URL链接（带域名）
- shortlink 文章的URL链接
- get_next 返回下一篇文章（Article模型）
- get_prev 返回上一篇文章（Article模型）

单页面 Flatpage
---------------

**基本属性：**

- id
- slug 英文唯一标识符
- title 页面标题 
- seotitle SEO标题
- seokey SEO关键词
- seodesc SEO描述
- template 页面内容页模板文件
- body 页面介绍（正常情况下是MARKDOWN格式）
- body_html 页面介绍HTML

**特殊属性：**

- link Tag的URL链接（带域名）
- shortlink Tag的URL链接

静态标签 Label
--------------

**基本属性：**

- id
- slug 英文唯一标识符
- title 标签标题
- html 标签HTML代码

友情链接 FriendLink
-------------------

**基本属性：**

- id
- anchor 锚文本
- title 鼠标移过时显示的标题
- url 链接URL
- actived 是否有效
- note 备注信息

重定向 Redirect
---------------

**基本属性：**

- id
- old_path 需要重定向的旧路径
- new_path 要重定向到的新路径
- note 备注信息

用户 User
---------

**基本属性：**

- id
- email 电子邮件
- username 用户名
- name 昵称
- role 所属角色
- password_hash 密码HASH值
- confirmed 是否确认
- about_me 自我介绍
- member_since 注册时间
- last_seen 上次登陆时间
- avatar_hash 头像HASH值

角色 Role
---------

**基本属性：**

- id
- name 角色名称
- default 是否为默认角色
- permissions 角色权限值
- users 角色对应的用户列表

**可调用的方法：**

- ``insert_roles`` 插入默认的角色分组信息

