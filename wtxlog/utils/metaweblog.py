# -*- coding: utf-8 -*-

import re
from datetime import datetime
from xmlrpclib import Fault

from functools import wraps
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

from flask import url_for, current_app, g
from .upload import SaveUploadFile
from ..models import db, User, Article as Post, Category

# 删除为知笔记的尾巴
pattern_wiz = re.compile(r'''<br\s?/><br\s?/><div><a.*href="http://www.wiz.cn.*">.*</a></div><br\s?/><br\s?/>''', re.I)


def checkauth(pos=1):
    def _decorate(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):

            username = args[pos + 0]
            password = args[pos + 1]

            # user = User.query.filter_by(email=username).first()
            errmsg, user = User.authenticate(username, password)
            if errmsg is not None:
                raise ValueError(errmsg)
            g.auth_user = user

            args = args[0:pos] + args[pos + 2:]
            return f(*args, **kwargs)
        return _wrapper
    return _decorate


def post_struct(entry):
    """post struct"""

    if not entry:
        raise Fault(-1, 'Post does not exist')

    categories = [entry.category.name, ]

    struct = {
        'postid': str(entry.id),
        'title': entry.title,
        'description': entry.body_html,
        'dateCreated': entry.created,
        'categories': categories,
    }

    return struct


# -------------------------------------------------------------------------------
# blogger
# -------------------------------------------------------------------------------

@checkauth()
def blogger_getUsersBlogs(discard):
    SITE_NAME = current_app.config.get('SITE_NAME')
    return [{'blogid': '31415926',
             'url': url_for('main.index', _external=True),
             'blogName': SITE_NAME,
             'isAdmin': True,
             'xmlrpc': url_for('main.xmlrpc', _external=True)}]


@checkauth(pos=2)
def blogger_deletePost(appkey, postid, publish=False):
    post = Post.query.get(postid)
    if post:
        db.session.delete(post)
        db.session.commit()
    return True


# -------------------------------------------------------------------------------
# metaWeblog
# -------------------------------------------------------------------------------

@checkauth()
def metaWeblog_newPost(blogid, struct, publish):
    """发布新博客"""
    _post = struct

    category_id = None
    category_name = _post['categories'][0] if _post['categories'] else None

    if category_name:
        category = Category.query.filter_by(name=category_name).first()
    else:
        category = Category.query.first()

    if isinstance(category, Category):
        category_id = category.id
    else:
        raise Fault(-1, 'There have no category found. Please add a new one.')

    content = pattern_wiz.sub('', _post['description'])
    post = Post()
    post.title = _post['title']
    post.body = content
    post.category_id = category_id
    post.author = g.auth_user
    if g.auth_user.is_administrator():
        post.published = True
    # post.source = u'metaWeblog'
    post.created = datetime.now()
    post.last_modified = post.created
    # more_start = post.content.find('<!--more-->')
    db.session.add(post)
    db.session.commit()

    return str(post.id)


@checkauth()
def metaWeblog_editPost(postid, struct, publish):
    """修改（更新）博客"""
    _post = struct

    category_id = None
    category_name = _post['categories'][0] if _post['categories'] else None

    if category_name:
        category = Category.query.filter_by(name=category_name).first()
        category_id = category.id

    post = Post.query.get(postid)

    if post is not None:
        content = pattern_wiz.sub('', _post['description'])
        post.title = _post['title']
        if category_id and post.category_id != category_id:
            post.category_id = category_id
        post.body = content
        post.last_modified = datetime.now()
        db.session.add(post)
        db.session.commit()
        return True
    else:
        raise Fault(-1, 'The post that you edit does not exist yet.')


@checkauth()
def metaWeblog_newMediaObject(blogid, struct):
    """多媒体文件上传，比如图片"""

    IMAGE_TYPES = {
        'image/jpeg': '.jpg',
        'image/png': '.png',
        'image/gif': '.gif',
    }

    media = struct
    fext = IMAGE_TYPES.get(media['type'])

    # data为二进制内容
    data = media['bits'].data

    # 这部分根据情况自定义
    obj = SaveUploadFile(fext, data)
    url = obj.save()
    return {'url': url}


@checkauth()
def metaWeblog_getCategories(blogid):
    """获取目录列表"""

    categories = Category.query.all()

    return [{
        'categoryId': category.id,
        'categoryName': category.name,
        'categoryDescription': category.seodesc,
        'description': category.seodesc} for category in categories]


@checkauth()
def metaWeblog_getPost(postid):

    post = Post.query.get(postid)

    if post:
        return post_struct(post)
    else:
        raise Fault(-1, 'The post that you get does not exist.')


@checkauth()
def metaWeblog_getRecentPosts(blogid, num=20):

    posts = Post.query.limit(num).all()
    return [post_struct(post) for post in posts]


# ------------------------------------------------------------------------------


class BlogXMLRPCDispatcher(SimpleXMLRPCDispatcher):

    def __init__(self, funcs):
        # "UTF-8" must be upper
        SimpleXMLRPCDispatcher.__init__(self, True, 'UTF-8')
        self.funcs = funcs
        self.register_introspection_functions()


blog_dispatcher = BlogXMLRPCDispatcher({
    'blogger.getUsersBlogs': blogger_getUsersBlogs,
    'blogger.deletePost': blogger_deletePost,

    'metaWeblog.newPost': metaWeblog_newPost,
    'metaWeblog.editPost': metaWeblog_editPost,
    'metaWeblog.getCategories': metaWeblog_getCategories,
    'metaWeblog.getPost': metaWeblog_getPost,
    'metaWeblog.getRecentPosts': metaWeblog_getRecentPosts,
    'metaWeblog.newMediaObject': metaWeblog_newMediaObject,
})
