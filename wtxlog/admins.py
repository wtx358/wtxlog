# -*- coding: utf-8 -*-

from urllib import unquote
from datetime import datetime
from flask import redirect, url_for, Markup, flash
from flask.ext.login import current_user, login_required
from flask.ext.admin import Admin, AdminIndexView, BaseView, expose, helpers
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from webhelpers.html import HTML
from webhelpers.html.tags import link_to

from wtforms.fields import SelectField, TextAreaField
from .utils.helpers import baidu_ping
from .utils.widgets import MarkitupTextAreaField, CKTextAreaField
from .ext import cache
from .models import *

from config import Config

BODY_FORMAT = Config.BODY_FORMAT
if BODY_FORMAT == 'html':
    EDITOR_WIDGET = CKTextAreaField
else:
    EDITOR_WIDGET = MarkitupTextAreaField

cache_key = Config.CACHE_KEY


def cache_delete(key):
    keys = [cache_key % key, 'mobile_%s' % (cache_key % key)]
    for _key in keys:
        cache.delete(_key)


def format_datetime(self, request, obj, fieldname, *args, **kwargs):
    return getattr(obj, fieldname).strftime("%Y-%m-%d %H:%M")


def view_on_site(self, request, obj, fieldname, *args, **kwargs):
    return Markup('%s%s' % (
        HTML.i(style='margin-right:5px;', class_='icon icon-eye-open'),
        link_to(u'View', obj.link, target='_blank'),
    ))


class MyAdminIndexView(AdminIndexView):

    @expose('/')
    @login_required
    def index(self):
        if not current_user.is_authenticated():
            return redirect(url_for('account.login'))
        return super(MyAdminIndexView, self).index()


# Customized Post model admin
class ArticleAdmin(sqla.ModelView):

    create_template = "admin/model/a_create.html"
    edit_template = "admin/model/a_edit.html"

    column_list = ('title', 'category', 'tags', 'published', 'ontop',
            'recommend', 'created', 'view_on_site')

    form_excluded_columns = ('author', 'body_html', 'hits', 'created',
                             'last_modified',)

    column_searchable_list = ('title',)

    column_formatters = dict(
            view_on_site=view_on_site,
            created=format_datetime,
    )

    form_create_rules = (
            'title', 'seotitle', 'category', 'topic', 'tags', 'body',
            'summary', 'published', 'ontop', 'recommend', 'seokey',
            'seodesc', 'thumbnail', 'thumbnail_big', 'template',
    )
    form_edit_rules = form_create_rules

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET,
                          summary=TextAreaField)

    form_widget_args = {
        'title': {'style': 'width:480px;'},
        'slug': {'style': 'width:480px;'},
        'seotitle': {'style': 'width:480px;'},
        'seokey': {'style': 'width:480px;'},
        'seodesc': {'style': 'width:480px; height:80px;'},
        'thumbnail': {'style': 'width:480px;'},
        'thumbnail_big': {'style': 'width:480px;'},
        'template': {'style': 'width:480px;'},
        'summary': {'style': 'width:680px; height:80px;'},
    }

    # Model handlers
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.author_id = current_user.id
            model.created = datetime.now()
            model.last_modified = model.created
        else:
            model.last_modified = datetime.now()

    def after_model_change(self, form, model, is_created):
        # 如果发布新文章，则PING通知百度
        if is_created and model.published:
            baidu_ping(model.link)

        # 清除缓存，以便可以看到最新内容
        cache_delete(model.shortlink)

    def is_accessible(self):
        return current_user.is_administrator()

    @action('pingbaidu', 'Ping to Baidu')
    def action_ping_baidu(self, ids):
        for id in ids:
            obj = Article.query.get(id)
            baidu_ping(obj.link)
        flash(u'PING请求已发送，请等待百度处理')


class CategoryAdmin(sqla.ModelView):

    create_template = "admin/model/a_create.html"
    edit_template = "admin/model/a_edit.html"

    column_list = ('name', 'longslug', 'seotitle', 'view_on_site')

    column_searchable_list = ('slug', 'longslug', 'name')

    form_excluded_columns = ('articles', 'body_html', 'longslug', 'children')

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET)

    column_formatters = dict(view_on_site=view_on_site)

    form_widget_args = {
        'slug': {'style': 'width:320px;'},
        'name': {'style': 'width:320px;'},
        'thumbnail': {'style': 'width:480px;'},
        'seotitle': {'style': 'width:480px;'},
        'seokey': {'style': 'width:480px;'},
        'seodesc': {'style': 'width:480px; height:80px;'},
        'template': {'style': 'width:480px;'},
        'article_template': {'style': 'width:480px;'},
    }

    # Model handlers
    def on_model_delete(self, model):
        if model.count > 0:
            raise Exception('Category <%s> is not empty.' % model.name)

    def on_model_change(self, form, model, is_created):
        if not model.id:
            c = Category.query.filter_by(name=model.name).first()
            if c:
                raise Exception('Category <%s> is already exist' % c.name)

            if not model.seotitle:
                model.seotitle = model.name

            if not model.seokey:
                model.seokey = model.name

    def after_model_change(self, form, model, is_created):
        cache_delete(model.shortlink)

    def is_accessible(self):
        return current_user.is_administrator()


class TagAdmin(sqla.ModelView):

    create_template = "admin/model/a_create.html"
    edit_template = "admin/model/a_edit.html"

    column_list = ('name', 'seotitle', 'seokey', 'view_on_site')

    column_searchable_list = ('name',)

    form_excluded_columns = ('articles', 'body_html')

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET)

    column_formatters = dict(view_on_site=view_on_site)

    form_widget_args = {
        'slug': {'style': 'width:320px;'},
        'name': {'style': 'width:320px;'},
        'thumbnail': {'style': 'width:480px;'},
        'seotitle': {'style': 'width:480px;'},
        'seokey': {'style': 'width:480px;'},
        'seodesc': {'style': 'width:480px; height:80px;'},
        'template': {'style': 'width:480px;'},
    }

    # Model handlers
    def on_model_change(self, form, model, is_created):
        if not model.id:
            t = Tag.query.filter_by(name=model.name).first()
            if t:
                raise Exception('Tag "%s" already exist' % t.name)

            if not model.seotitle:
                model.seotitle = model.name

            if not model.seokey:
                model.seokey = model.name

    def after_model_change(self, form, model, is_created):
        # 中文的路径特别需要注意
        cache_delete(model.shortlink)

    def is_accessible(self):
        return current_user.is_administrator()


class TopicAdmin(sqla.ModelView):

    create_template = "admin/model/a_create.html"
    edit_template = "admin/model/a_edit.html"

    column_list = ('name', 'slug', 'seotitle', 'view_on_site')

    form_excluded_columns = ('articles', 'body_html')

    column_searchable_list = ('slug', 'name')

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET)

    column_formatters = dict(view_on_site=view_on_site)

    form_widget_args = {
        'slug': {'style': 'width:320px;'},
        'name': {'style': 'width:320px;'},
        'thumbnail': {'style': 'width:480px;'},
        'seotitle': {'style': 'width:480px;'},
        'seokey': {'style': 'width:480px;'},
        'seodesc': {'style': 'width:480px; height:80px;'},
        'template': {'style': 'width:480px;'},
    }

    # Model handlers
    def on_model_change(self, form, model, is_created):
        if not model.id:
            t = Topic.query.filter_by(name=model.name).first()
            if t:
                raise Exception('Topic "%s" already exist' % t.name)

            if not model.seotitle:
                model.seotitle = model.name

            if not model.seokey:
                model.seokey = model.name

    def after_model_change(self, form, model, is_created):
        cache_delete(model.shortlink)

    def is_accessible(self):
        return current_user.is_administrator()

class FlatpageAdmin(sqla.ModelView):

    create_template = "admin/model/a_create.html"
    edit_template = "admin/model/a_edit.html"

    column_list = ('title', 'slug', 'seotitle', 'view_on_site')

    column_searchable_list = ('slug', 'title', )

    column_formatters = dict(view_on_site=view_on_site)

    form_excluded_columns = ('body_html', )

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET)

    form_widget_args = {
        'title': {'style': 'width:480px;'},
        'slug': {'style': 'width:320px;'},
        'seotitle': {'style': 'width:480px;'},
        'seokey': {'style': 'width:480px;'},
        'seodesc': {'style': 'width:480px; height:80px;'},
        'template': {'style': 'width:480px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()

    def on_model_change(self, form, model, is_created):
        pass

    def after_model_change(self, form, model, is_created):
        cache_delete(model.shortlink)


class FriendLinkAdmin(sqla.ModelView):

    column_exclude_list = ['note']

    column_searchable_list = ('anchor', 'title', 'url')

    form_overrides = dict(note=TextAreaField)

    form_widget_args = {
        'anchor': {'style': 'width:320px;'},
        'title': {'style': 'width:320px;'},
        'url': {'style': 'width:480px;'},
        'note': {'style': 'width:480px; height:80px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


class LinkAdmin(sqla.ModelView):

    column_exclude_list = ['note']

    form_overrides = dict(note=TextAreaField)

    form_widget_args = {
        'title': {'style': 'width:320px;'},
        'url': {'style': 'width:480px;'},
        'note': {'style': 'width:480px; height:80px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


class LabelAdmin(sqla.ModelView):

    column_list = ('slug', 'title')

    column_searchable_list = ('slug', 'title')

    form_overrides = dict(html=TextAreaField)

    form_widget_args = {
        'slug': {'style': 'width:480px;'},
        'title': {'style': 'width:480px;'},
        'html': {'style': 'width:640px; height:320px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


class RedirectAdmin(sqla.ModelView):

    column_searchable_list = ('old_path', 'new_path')

    form_overrides = dict(note=TextAreaField)

    form_widget_args = {
        'old_path': {'style': 'width:320px;'},
        'new_path': {'style': 'width:320px;'},
        'note': {'style': 'width:480px; height:80px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


class UserAdmin(sqla.ModelView):

    column_list = ('email', 'username', 'name', 'role', 'confirmed')

    form_excluded_columns = ('password_hash', 'avatar_hash', 'articles', 'member_since', 'last_seen')

    column_searchable_list = ('email', 'username', 'name')

    form_overrides = dict(about_me=TextAreaField)

    form_widget_args = {
        'about_me': {'style': 'width:480px; height:80px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


# init
admin = Admin(index_view=MyAdminIndexView(), base_template="admin/my_master.html")

# add views
admin.add_view(TopicAdmin(Topic, db.session))
admin.add_view(CategoryAdmin(Category, db.session))
admin.add_view(TagAdmin(Tag, db.session))
admin.add_view(ArticleAdmin(Article, db.session))
admin.add_view(FlatpageAdmin(Flatpage, db.session))

admin.add_view(LabelAdmin(Label, db.session))

admin.add_view(FriendLinkAdmin(FriendLink, db.session))
admin.add_view(RedirectAdmin(Redirect, db.session))

admin.add_view(UserAdmin(User, db.session))

