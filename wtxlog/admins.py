# -*- coding: utf-8 -*-

from datetime import datetime
from flask import redirect, url_for, Markup, flash
from flask.ext.babelex import lazy_gettext as _
from flask.ext.login import current_user, login_required
from flask.ext.admin import Admin, AdminIndexView, expose
from flask.ext.admin.contrib import sqla
from flask.ext.admin.actions import action
from flask.ext.admin.form.fields import Select2Field
from webhelpers.html import HTML
from webhelpers.html.tags import link_to

from wtforms.fields import TextAreaField
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
        link_to(_('View'), obj.link, target='_blank'),
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

    column_formatters = dict(view_on_site=view_on_site,
                             created=format_datetime)

    form_create_rules = (
        'title', 'seotitle', 'category', 'topic', 'tags', 'body',
        'summary', 'published', 'ontop', 'recommend', 'seokey',
        'seodesc', 'thumbnail', 'thumbnail_big', 'template',
    )
    form_edit_rules = form_create_rules

    form_overrides = dict(seodesc=TextAreaField, body=EDITOR_WIDGET,
                          summary=TextAreaField)

    column_labels = dict(
        title=_('Title'),
        seotitle=_('SEOTitle'),
        category=_('Category'),
        topic=_('Topic'),
        tags=_('Tags'),
        body=_('Body'),
        summary=_('Summary'),
        published=_('Published'),
        ontop=_('Ontop'),
        recommend=_('Recommend'),
        seokey=_('SEO Keyword'),
        seodesc=_('SEO Description'),
        thumbnail=_('Thumbnail'),
        thumbnail_big=_('Big Thumbnail'),
        template=_('Template'),
        created=_('Created'),
        view_on_site=_('View on Site'),
    )

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

    column_labels = dict(
        parent=_('Parent'),
        slug=_('Slug'),
        longslug=_('LongSlug'),
        name=_('Name'),
        seotitle=_('SEOTitle'),
        body=_('Body'),
        seokey=_('SEO Keyword'),
        seodesc=_('SEO Description'),
        thumbnail=_('Thumbnail'),
        template=_('Template'),
        article_template=_('Template of Articles'),
        view_on_site=_('View on Site'),
    )

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

    column_labels = dict(
        slug=_('Slug'),
        name=_('Name'),
        seotitle=_('SEOTitle'),
        body=_('Body'),
        seokey=_('SEO Keyword'),
        seodesc=_('SEO Description'),
        thumbnail=_('Thumbnail'),
        template=_('Template'),
        view_on_site=_('View on Site'),
    )

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

    column_labels = dict(
        slug=_('Slug'),
        name=_('Name'),
        seotitle=_('SEOTitle'),
        body=_('Body'),
        seokey=_('SEO Keyword'),
        seodesc=_('SEO Description'),
        thumbnail=_('Thumbnail'),
        template=_('Template'),
        view_on_site=_('View on Site'),
    )

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

    column_labels = dict(
        slug=_('Slug'),
        title=_('Title'),
        seotitle=_('SEOTitle'),
        body=_('Body'),
        seokey=_('SEO Keyword'),
        seodesc=_('SEO Description'),
        thumbnail=_('Thumbnail'),
        template=_('Template'),
        view_on_site=_('View on Site'),
    )

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

    column_labels = dict(
        anchor=_('Anchor Text'),
        title=_('Title'),
        url=_('URL'),
        actived=_('Actived'),
        order=_('Order'),
        note=_('Note'),
    )

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

    column_labels = dict(
        slug=_('Slug'),
        title=_('Title'),
        html=_('Html Code'),
    )

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

    column_labels = dict(
        old_path=_('Old Path'),
        new_path=_('New Path'),
        note=_('Note'),
    )

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

    column_labels = dict(
        email=_('Email'),
        username=_('Username'),
        name=_('Nickname'),
        confirmed=_('Confirmed'),
        about_me=_('About Me'),
        role=_('Role'),
    )

    form_widget_args = {
        'about_me': {'style': 'width:480px; height:80px;'},
    }

    def is_accessible(self):
        return current_user.is_administrator()


class SettingAdmin(sqla.ModelView):

    form_overrides = dict(
        rawvalue=TextAreaField,
        formatter=Select2Field,
        description=TextAreaField,
    )

    column_labels = dict(
        name=_('Name'),
        rawvalue=_('Raw Value'),
        formatter=_('Formatter'),
        builtin=_('Builtin'),
        description=_('Description'),
    )

    form_args = dict(
        formatter=dict(choices=Setting.FORMATS)
    )

    def is_accessible(self):
        return current_user.is_administrator()


# init
admin = Admin(index_view=MyAdminIndexView(),
              name=_('Admin'),
              base_template="admin/my_master.html")

# add views
admin.add_view(TopicAdmin(Topic, db.session, name=_('Topic')))
admin.add_view(CategoryAdmin(Category, db.session, name=_('Category')))
admin.add_view(TagAdmin(Tag, db.session, name=_('Tag')))
admin.add_view(ArticleAdmin(Article, db.session, name=_('Article')))
admin.add_view(FlatpageAdmin(Flatpage, db.session, name=_('Flatpage')))

admin.add_view(LabelAdmin(Label, db.session, name=_('Snippet')))

admin.add_view(FriendLinkAdmin(FriendLink, db.session, name=_('FriendLink')))
admin.add_view(RedirectAdmin(Redirect, db.session, name=_('Redirect')))

admin.add_view(SettingAdmin(Setting, db.session, name=_('Setting')))

admin.add_view(UserAdmin(User, db.session, name=_('User')))
