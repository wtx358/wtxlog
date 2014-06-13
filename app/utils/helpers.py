# -*- coding: utf-8 -*-

from flask import current_app
from flask.ext.themes import render_theme_template, get_theme
from ..models import Category, Tag


def get_current_theme():
    return get_theme(current_app.config.get('THEME') or 'default')


def render_template(template, **context):
    return render_theme_template(get_current_theme(), template, **context)


def get_category_ids(longslug):
    """"返回指定longslug开头的所有栏目的ID列表"""
    cates = Category.query.filter(Category.longslug.startswith(longslug))
    if cates:
        return [cate.id for cate in cates.all()]
    else:
        return []

