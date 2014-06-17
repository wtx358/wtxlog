# -*- coding: utf-8 -*-

import os
import json
import datetime
from urllib import quote, unquote

from flask import request, url_for, redirect, current_app, make_response, abort
from werkzeug.contrib.atom import AtomFeed
from webhelpers.paginate import Page, PageURL
from flask.ext.mobility.decorators import mobile_template

from ..utils.helpers import render_template, get_category_ids
from ..utils.upload import SaveUploadFile
from ..utils.metaweblog import blog_dispatcher
from ..ext import cache
from ..models import db, Article, Category, Tag, Flatpage, Topic, Role
from . import main

IMAGE_TYPES = {
    'image/jpeg': '.jpg',
    'image/png' : '.png',
    'image/gif' : '.gif',
}


@main.route('/deploy/')
def deploy():
    db.create_all()
    Role.insert_roles()
    return 'deployed'


@main.route('/')
@mobile_template('{mobile/}%s')
@cache.cached()
def index(template):
    _template = template % 'index.html'
    blog_mode = current_app.config.get("BLOG_MODE")
    if blog_mode:
        page = int(request.args.get('page', 1))

        _url = PageURL(url_for('main.index'), {"page": page})
        _query = Article.query.public()
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)
        articles = pagination.items

        return render_template(_template,
                               articles=articles, 
                               pagination=pagination)
    else:
        return render_template(_template)


@main.route('/article/<int:article_id>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def article(template, article_id):
    article = Article.query.get_or_404(article_id)

    if not article.published:
        abort(403)

    _template = template % (article.category.article_template or \
            article.template or 'article.html')
    return render_template(_template, article=article)


@main.route('/category/<path:longslug>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def category(template, longslug):
    category = Category.query.filter_by(longslug=longslug).first_or_404()
    cate_ids = get_category_ids(longslug)

    page = int(request.args.get('page', 1))

    _url = PageURL(category.link, {"page": page})
    _query = Article.query.public().filter(Article.category_id.in_(cate_ids))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (category.template or 'category.html')
    return render_template(_template,
                           category=category, 
                           pagination=pagination,
                           articles=articles)


@main.route('/archives/<int:year>/<int:month>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def archives(template, year, month):
    page = int(request.args.get('page', 1))

    _url = PageURL(url_for('main.archives', year=year, month=month), {"page": page})
    _query = Article.query.archives(year, month)
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % 'archives.html'
    return render_template(_template,
                           pagination=pagination,
                           articles=articles,
                           year = year,
                           month = month)


@main.route('/tag/')
def tags_():
    return redirect(url_for('.tags'), code=301)


@main.route('/tags/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def tags(template):
    _template = template % 'tags.html'
    return render_template(_template)


@main.route('/tag/<name>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def tag(template, name):
    '''
    :param template:
        模板文件，此参数自动传入
    :param name:
        Tag名称，若为非ASCII字符，一般是经过URL编码的
    '''
    # 若name为非ASCII字符，传入时一般是经过URL编码的
    # 若name为URL编码，则需要解码为Unicode
    # URL编码判断方法：若已为URL编码, 再次编码会在每个码之前出现`%25`
    _name = name.encode('utf-8')
    if quote(_name).count('%25') > 0:
        name = unquote(_name)

    tag = Tag.query.filter_by(name=name).first_or_404()
    
    page = int(request.args.get('page', 1))
    
    _url = PageURL(url_for('main.tag', name=name), {"page": page})
    _query = Article.query.public().filter(Article.tags.any(id=tag.id))
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (tag.template or 'tag.html')
    return render_template(_template,
                           tag=tag, 
                           pagination=pagination,
                           articles=articles)


@main.route('/topic/<slug>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def topic(template, slug):
    topic = Topic.query.filter_by(slug=slug).first_or_404()

    page = int(request.args.get('page', 1))

    _url = PageURL(url_for('main.topic', slug=slug), {"page": page})
    _query = Article.query.public().filter(Article.topic_id==topic.id)
    pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

    articles = pagination.items

    _template = template % (topic.template or 'topic.html')
    return render_template(_template,
                           topic=topic, 
                           pagination=pagination,
                           articles=articles)


@main.route('/flatpage/<slug>/')
@mobile_template('{mobile/}%s')
@cache.cached(86400)
def flatpage(template, slug):
    flatpage = Flatpage.query.filter_by(slug=slug).first_or_404()
    _template = template % (flatpage.template or 'flatpage.html')
    return render_template(_template, flatpage=flatpage)


@main.route('/search/')
@mobile_template('{mobile/}%s')
def search(template):
    page = int(request.args.get('page', 1))
    keyword = request.args.get('keyword', None)
    pagination = None
    articles = None
    if keyword:
        _url = PageURL(url_for('main.search'), 
                       {"page": page, "keyword": keyword.encode('utf-8')})
        _query = Article.query.search(keyword)
        pagination = Page(_query, page=page, items_per_page=Article.PER_PAGE, url=_url)

        articles = pagination.items
    
    _template = template % 'search.html'
    return render_template(_template,
                           articles=articles, 
                           keyword = keyword,
                           pagination=pagination)


@main.route('/sitemap.xsl')
def sitemap_xsl():
    response = make_response(render_template('sitemap.xsl'))
    response.headers["Content-Type"] = "text/xml"
    return response


@main.route('/sitemap.xml', methods=['GET'])
@cache.cached(86400)
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []

    pages.append(
        [url_for('.index', _external=True), 
         datetime.datetime.now().isoformat(), 
         'weekly', 1],
    )

    # categories
    cates = Category.query.all()

    for cate in cates:
        pages.append([cate.link,
                      '', #datetime.datetime.now().isoformat(),
                      'weekly',
                      0.8])

    # tags
    tags = Tag.query.all()

    for tag in tags:
        pages.append([tag.link,
                      '', #datetime.datetime.now().isoformat(),
                      'weekly',
                      0.6])

    # articles model pages
    articles = Article.query.public().all()

    for article in articles:
        url = article.link
        modified_time = article.last_modified.isoformat()
        pages.append([url, modified_time, 'weekly', 0.5])
    
    sitemap_xml = render_template('sitemap.xml', pages=pages)
    res = make_response(sitemap_xml)
    res.headers["Content-Type"] = "application/xml"

    return res


@main.route('/feed/')
def feed():
    site_name = current_app.config.get('SITE_NAME')

    feed = AtomFeed(
        u"%s Recent Articles" % site_name, 
        feed_url=request.url, 
        url=request.url_root,
    )

    articles = Article.query.public().limit(10).all()

    for article in articles:
        feed.add(
            article.title, 
            unicode(article.summary),
            content_type='html',
            author=article.author,
            url=article.link,
            updated=article.last_modified,
            published=article.created
        )

    return feed.get_response()


@main.route('/upload/', methods=['POST', 'OPTIONS'])
def upload():
    ''' 文件上传函数 '''

    result = {"err":"", "msg":{"url":"","localfile":""}} 
    fname = ''
    fext = ''
    data = None

    if request.method=='POST' and 'filedata' in request.files:
        # 传统上传模式，IE浏览器使用这种模式
        fileobj = request.files['filedata']
        result["msg"]["localfile"] = fileobj.filename
        fname, fext = os.path.splitext(fileobj.filename)
        data = fileobj.read()
    elif request.headers.has_key('CONTENT_DISPOSITION'):
        # HTML5上传模式，FIREFOX等默认使用此模式
        pattern = re.compile(r"""\s.*?\s?filename\s*=\s*['|"]?([^\s'"]+).*?""", re.I)
        filenames = pattern.findall(request.headers.get('CONTENT_DISPOSITION'))
        if len(filenames) == 1:
            result["msg"]["localfile"] = urllib.unquote(filenames[0])
            fname, fext = os.path.splitext(filenames[0])
        data = request.data

    ONLINE = False
    if ONLINE:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
    else:
        obj = SaveUploadFile(fext, data)
        url = obj.save()
        result["msg"]["url"] = '!%s' % url
        pass

    return json.dumps(result)
    

@main.route('/uploadremote/', methods=['POST', 'OPTIONS'])
def uploadremote():
    """ 
    xheditor保存远程图片简单实现
    URL用"|"分隔，返回的字符串也是用"|"分隔
    返回格式是字符串，不是JSON格式
    """
    localdomain_re = re.compile("""https?:\/\/[^\/]*?(bcs\.duapp\.com)\/""", re.I)
    imageTypes = {'gif':'.gif', 'jpeg':'.jpg', 'jpg':'.jpg', 'png':'.png'}
    urlout = []
    result = ''
    srcUrl = request.form.get('urls', None)
    if srcUrl:
        urls = srcUrl.split('|')
        for url in urls:
            if not localdomain_re.search(url.strip()):
                downfile = urllib.urlopen(url)
                fext = imageTypes[downfile.headers.getsubtype().lower()]

                urlreturn = ''

                if ONLINE:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                else:
                    obj = SaveUploadFile(fext, downfile.read())
                    urlreturn = obj.save()
                    pass

                urlout.append(urlreturn)
            else:
                urlout.append(url)
    result = '|'.join(urlout)
    return result


@main.route('/xmlrpc/', methods=['POST', 'OPTIONS'])
def xmlrpc():
    """
    author: digwtx <wtx358@qq.com>

    firefox-scribefire and Blogilo passed.

    Reference:

    * <http://codex.wordpress.org.cn/XML-RPC_MetaWeblog_API>
    * <http://blog.csdn.net/priderock/article/details/1754503>
    """

    #return blog_dispatcher._marshaled_dispatch(request.data)
    response_data = blog_dispatcher._marshaled_dispatch(request.data)
    return current_app.response_class(response_data,
                                      content_type='text/xml')


@main.route('/ckupload/', methods=['POST', 'OPTIONS'])
def ckupload():
    """CKEditor file upload"""
    data = None
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")

    if request.method=='POST' and 'upload' in request.files:
        # 传统上传模式，IE浏览器使用这种模式
        fileobj = request.files['upload']
        data = fileobj.read()
        fname, fext = os.path.splitext(fileobj.filename)
        if fext.lower() in ('.gif', '.jpg', '.jpeg', '.png'):
            _fext = fext
        else:
            _fext = fileobj.filename
        try:
            obj = SaveUploadFile(_fext, data)
            url = obj.save()
        except:
            error = 'upload error'
    else:
        error = 'post error'

    res = """<script type="text/javascript">
  window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
</script>""" % (callback, url, error)

    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

