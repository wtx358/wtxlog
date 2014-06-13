# -*- coding: utf-8 -*-

from flask import request, jsonify, redirect
from flask.ext.mobility.decorators import mobile_template
from ..utils.helpers import render_template
from ..models import db, Redirect
from . import main


@main.app_errorhandler(403)
@mobile_template('{mobile/}%s')
def forbidden(e, template):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    _template = template % 'errors/403.html'
    return render_template(_template), 403


@main.app_errorhandler(404)
@mobile_template('{mobile/}%s')
def page_not_found(e, template):
    try:
        _r = Redirect.query.filter_by(old_path=request.path).first()
        if _r:
            return redirect(_r.new_path, code=301)
    except:
        pass

    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    _template = template % 'errors/404.html'
    return render_template(_template), 404


@main.app_errorhandler(500)
@mobile_template('{mobile/}%s')
def internal_server_error(e, template):
    try:
        db.session.rollback()
    except:
        pass
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    _template = template % 'errors/500.html'
    return render_template(_template), 500
