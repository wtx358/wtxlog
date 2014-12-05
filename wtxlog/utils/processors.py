# -*- coding: utf-8 -*-

import time
import random
import datetime

from flask import request, Markup, render_template_string
from flask.ext.restless.search import create_query
from ..models import db, Article, Category, Tag, FriendLink, Link, \
    Label, Topic, Setting
from helpers import get_category_ids


def utility_processor():
    """自定义模板处理器"""

    def archives():
        """
        返回从第一篇文章开始到现在所经历的月份列表
        """
        # archives = cache.get("archives")
        archives = None
        if archives is None:
            begin_post = Article.query.order_by('created').first()

            now = datetime.datetime.now()

            begin_s = begin_post.created if begin_post else now
            end_s = now

            begin = begin_s
            end = end_s

            total = (end.year - begin.year) * 12 - begin.month + end.month
            archives = [begin]

            date = begin
            for i in range(total):
                if date.month < 12:
                    date = datetime.datetime(date.year, date.month + 1, 1)
                else:
                    date = datetime.datetime(date.year + 1, 1, 1)
                archives.append(date)
            archives.reverse()
            # cache.set("archives", archives)
        return archives

    def model_query(model, search_params):
        '''
        模型复杂查询

        :param model:
            实例模型，比如Article, Category, Tag, etc.
        :param search_params:
            参数字典，为dict类型，参照flask-restless文档

        特别注意：使用这个方法进行查询，模型`__mapper_args__`的
        `order_by`定义将会失效，在模板中使用时需要特别注意。

        详细内容请参照Flask-Restless的文档
        '''
        # `is_single` is True when 'single' is a key in ``search_params`` and its
        # corresponding value is anything except those values which evaluate to
        # False (False, 0, the empty string, the empty list, etc.).
        is_single = search_params.get('single')
        query = create_query(db.session, model, search_params)
        if is_single:
            # may raise NoResultFound or MultipleResultsFound
            return query.one()
        return query.all()

    def category_lists(parent=None, limit=None):
        """
        返回栏目列表

        :param parent:
            父级栏目，`None`或者`Category`实例
        :param limit:
            返回的个数，`None`或者正整数
        """
        _query = Category.query.filter_by(parent=parent)
        if isinstance(limit, int):
            _query = _query.limit(limit)
        return _query.all()

    def tag_lists(limit=None):
        """
        返回标签列表

        :param limit:
            返回的个数，`None`或者正整数
        """
        _query = Tag.query
        if isinstance(limit, int):
            _query = _query.limit(limit)
        return _query.all()

    def topic_lists(limit=None):
        """
        返回专题列表

        :param limit:
            返回的个数，`None`或者正整数
        """
        _query = Topic.query
        if isinstance(limit, int):
            _query = _query.limit(limit)
        return _query.all()

    def category_tree():
        """
        返回栏目树形列表
        """
        return Category.tree()

    def get_related_articles(article_id, limit=10):
        """
        返回指定文章的相关文章列表

        根据Tag来筛选

        :param article_id:
            文章ID, 正整数
        :param limit:
            返回的个数, 正整数，默认为10
        """
        # 获取与本文章标签相同的所有文章ID
        article = Article.query.get(article_id)
        if article:
            ids = db.session.query('article_id') \
                            .from_statement('SELECT article_id FROM '
                                            'article_tags WHERE tag_id IN '
                                            '(SELECT tag_id FROM article_tags '
                                            'WHERE article_id=:article_id)') \
                            .params(article_id=article_id).all()

            article_ids = [_id[0] for _id in ids]
            article_ids = list(set(article_ids))

            if article_id in article_ids:
                article_ids.remove(article_id)

            random_ids = random.sample(article_ids, min(limit, len(article_ids)))

            if article_ids:
                return Article.query.public().filter(Article.id.in_(random_ids)).all()
        return None

    def get_latest_articles(category=None, limit=10):
        """
        返回最新文章列表

        :param category:
            当前栏目，`None`或者`Category`实例
        :param limit:
            返回的个数，正整数，默认为10
        """
        _query = Article.query.public()
        if isinstance(category, Category):
            cate_ids = get_category_ids(category.longslug)
            _query = _query.filter(Article.category_id.in_(cate_ids))
        return _query.limit(int(limit)).all()

    def get_top_articles(days=365, limit=10):
        """
        返回热门文章列表

        :param days:
            天数的范围，比如：一周7天，一个月30天。默认为一年
        :param limit:
            返回的个数，正整数，默认为10
        """
        criteria = []

        _start = datetime.date.today() - datetime.timedelta(days)
        criteria.append(Article.created >= _start)

        q = reduce(db.and_, criteria)
        return Article.query.public().filter(q) \
                                     .order_by(Article.hits.desc()) \
                                     .limit(int(limit)).all()

    def get_recommend_articles(category=None, limit=10):
        """
        返回推荐文章列表

        :param category:
            当前栏目，`None`或者`Category`实例
        :param limit:
            返回的个数，正整数，默认为10
        """
        _query = Article.query.public()
        if isinstance(category, Category):
            cate_ids = get_category_ids(category.longslug)
            _query = _query.filter(Article.category_id.in_(cate_ids))
        return _query.filter_by(recommend=True).limit(int(limit)).all()

    def get_thumbnail_articles(category=None, limit=10):
        """
        返回有缩略图的文章列表

        :param category:
            当前栏目，`None`或者`Category`实例
        :param limit:
            返回的个数，正整数，默认为10
        """
        _query = Article.query.public()
        if isinstance(category, Category):
            cate_ids = get_category_ids(category.longslug)
            _query = _query.filter(Article.category_id.in_(cate_ids))
        return _query.filter(Article.thumbnail.isnot(None)).limit(int(limit)).all()

    def get_articles_by_category(longslug='', limit=10, expand=True):
        """
        根据栏目路径返回文章列表

        :param longslug:
            栏目路径，字符串，不要以`/`结尾
        :param limit:
            返回的个数，整数
        :param expand:
            是否返回子栏目文章，`False`则只返回当前栏目的文章
        """
        _query = Article.query.public()
        category = Category.query.filter_by(longslug=longslug).first()
        if category:
            if expand:
                cate_ids = get_category_ids(longslug)
                _query = _query.filter(Article.category_id.in_(cate_ids))
            else:
                _query = _query.filter_by(category_id=category.id)
        return _query.limit(int(limit)).all()

    def friendlinks():
        """
        返回所有有效的友情链接列表
        """
        return FriendLink.query.filter_by(actived=True).all()

    def label(slug):
        """
        返回静态标签

        :param slug:
            英文标识符，unicode类型
        """
        s = Label.query.filter_by(slug=slug).first()
        return Markup(render_template_string(s.html)) if s is not None else ''

    return dict(
        Article=Article,
        Category=Category,
        Tag=Tag,
        Topic=Topic,
        FriendLink=FriendLink,
        Setting=Setting,
        model_query=model_query,
        archives=archives,
        get_category_ids=get_category_ids,
        get_latest_articles=get_latest_articles,
        get_top_articles=get_top_articles,
        get_recommend_articles=get_recommend_articles,
        get_thumbnail_articles=get_thumbnail_articles,
        get_related_articles=get_related_articles,
        get_articles_by_category=get_articles_by_category,
        category_tree=category_tree,
        category_lists=category_lists,
        tag_lists=tag_lists,
        topic_lists=topic_lists,
        friendlinks=friendlinks,
        label=label,
    )
