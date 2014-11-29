# -*- coding: utf-8 -*-

from flask import request
from ..models import db, Article
from . import api


@api.route('/gethits/')
def gethits():
    id = int(request.args.get('id', 0))
    article = Article.query.get(id)
    if article:
        article.hits += 1
        db.session.add(article)
        db.session.commit()
        return str(article.hits)
    return 'err'
