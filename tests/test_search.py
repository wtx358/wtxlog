# -*- encoding: utf-8 -*-

import datetime
import unittest
from flask import url_for
from wtxlog import create_app, db
from wtxlog.models import Article, Category, Tag, Role


class SearchTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_tags_search(self):
        tag1 = Tag(name=u'中国')
        tag2 = Tag(name=u'China')
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.commit()
        tags1 = Tag.query.search(u'中国')
        tags2 = Tag.query.search(u'China')
        self.assertTrue(tag1 in tags1)
        self.assertTrue(tag2 in tags2)

    def test_articles_search(self):
        category = Category(name=u'默认', slug='default1')
        db.session.add(category)
        db.session.commit()
        article = Article(title=u'我是中国人', category_id=category.id,
                          body='hello flask', created=datetime.datetime.now(),
                          last_modified=datetime.datetime.now())
        db.session.add(article)
        db.session.commit()
        articles = Article.query.search(u'中国')
        self.assertTrue(article in articles)
