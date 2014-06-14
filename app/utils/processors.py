# -*- coding: utf-8 -*-

import time
import random
import datetime

from flask import request, Markup, render_template_string
from ..models import db, Article, Category, Tag, FriendLink, Link, Label
from helpers import get_category_ids


def utility_processor():
    """自定义模板处理器"""
    def pager(page=1):
        """简单的分页路径生成，参考Flask-Admin"""
        args = request.args
        path = request.path
        kwargs = dict((arg, args[arg]) for arg in args)
        kwargs['page'] = unicode(page)
        if page==1:
            kwargs.pop('page')
        if kwargs:
            return '%s?%s' % (
                path,
                '&'.join(['%s=%s' % (arg,kwargs[arg]) for arg in kwargs]),
            )
        else:
            return path

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

    def category_lists(parent=None, limit=None):
        """
        返回栏目列表

        :param parent:
            父级栏目，`None`或者`Category`实例
        :param limit:
            返回的个数，`None`或者正整数
        """
        if limit:
            return Category.query.filter_by(parent=parent).limit(int(limit)).all()
        else:
            return Category.query.filter_by(parent=parent).all()

    def category_tree():
        """
        返回栏目树形列表
        """
        return Category.tree()

    def tag_lists(limit=None):
        """
        返回标签列表

        :param limit:
            返回的个数，`None`或者正整数
        """
        if limit:
            return Tag.query.limit(int(limit)).all()
        else:
            return Tag.query.all()

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
            article_ids = []
            for tag in article.tags:
                for a in tag.articles:
                    article_ids.append(a.id)
            article_ids = list(set(article_ids))
            if article_id in article_ids:
                article_ids.remove(article_id)
            random_ids = random.sample(article_ids, 
                                       min(limit, len(article_ids)))

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
        if isinstance(category, Category):
            cate_ids = get_category_ids(category.longslug)
            return Article.query.public().filter(Article.category_id.in_(cate_ids)) \
                                .limit(int(limit)).all()
        return Article.query.public().limit(int(limit)).all()

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
        if isinstance(category, Category):
            cate_ids = get_category_ids(category.longslug)
            return Article.query.public().filter(Article.category_id.in_(cate_ids)) \
                                .filter_by(recommend=True).limit(int(limit)).all()
        return Article.query.public().filter_by(recommend=True).limit(int(limit)).all()

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

    def get_articles_by_tag(name, limit=10):
        """
        根据Tag标签返回文章列表

        :param name:
            Tag标签名称，unicode类型
        :param limit:
            返回的个数，正整数
        """
        tag = Tag.query.filter_by(name=name).first()
        if tag:
            ids = [article.id for article in tag.articles]
            return Article.query.public().filter(Article.id.in_(ids)) \
                                         .limit(int(limit)).all()
        return []

    def get_articles_by_category(longslug, limit=10, showall=True):
        """
        根据栏目路径返回文章列表

        :param longslug:
            栏目路径，字符串，不要以`/`结尾
        :param limit:
            返回的个数，整数
        :param showall:
            是否返回子栏目文章，`False`则只返回当前栏目的文章
        """
        category = Category.query.filter_by(longslug=longslug).first()
        if category:
            if showall:
                cate_ids = get_category_ids(longslug)
                return Article.query.public() \
                                    .filter(Article.category_id.in_(cate_ids)) \
                                    .limit(int(limit)).all()
            else:
                return Article.query.public() \
                                    .filter_by(category_id=category.id) \
                                    .limit(int(limit)).all()
        return []

    return dict(
        pager=pager,
        archives=archives,
        category_lists=category_lists,
        category_tree=category_tree,
        tag_lists=tag_lists,
        get_related_articles=get_related_articles,
        get_latest_articles=get_latest_articles,
        get_top_articles=get_top_articles,
        get_recommend_articles=get_recommend_articles,
        get_articles_by_category=get_articles_by_category,
        get_articles_by_tag=get_articles_by_tag,
        friendlinks=friendlinks,
        label=label,
    )
