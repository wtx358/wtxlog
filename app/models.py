# -*- coding: utf-8 -*-

import hashlib
from datetime import datetime
from werkzeug import cached_property
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from webhelpers.text import remove_formatting, truncate

from flask.ext.sqlalchemy import BaseQuery

from flask import current_app, request, url_for
from flask.ext.login import UserMixin, AnonymousUserMixin

from .ext import db
from .utils.filters import markdown_filter
from config import Config

BODY_FORMAT = Config.BODY_FORMAT


class Permission:
    '''定义角色拥有的权限'''

    #写的文章是草稿，不公开
    WRITE_ARTICLES = 0x04

    #可以公开文章
    PUBLISH_ARTICLES = 0x08

    #管理后台的权限
    ADMINISTER = 0x80


class Role(db.Model):

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    __mapper_args__ = {'order_by': [id.desc()]}

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.WRITE_ARTICLES |
                          Permission.PUBLISH_ARTICLES, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name
    
    def __unicode__(self):
        return self.name


class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    name = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey(Role.id))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    about_me = db.Column(db.String(1000))
    member_since = db.Column(db.DateTime(), default=datetime.now)
    last_seen = db.Column(db.DateTime(), default=datetime.now)
    avatar_hash = db.Column(db.String(32))

    __mapper_args__ = {'order_by': [confirmed.desc(), id.desc()]}

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config.get('APP_ADMIN'):
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @staticmethod
    def authenticate(username, password):
        """
        验证用户：如果成功，返回User模型，否则返回None

        :param username: 用户名或者电子邮件地址
        :param password: 用户密码
        """
        user = User.query.filter(db.or_(User.username==username,
            User.email==username)).first()
        if user and user.verify_password(password):
            return user
        return None

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER) & self.confirmed

    def ping(self):
        self.last_seen = datetime.now()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % (self.name or self.username)

    def __unicode__(self):
        return self.name or self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


# Create M2M table
article_tags_table = db.Table(
    'article_tags', 
    db.Model.metadata, 
    db.Column('article_id', db.Integer, db.ForeignKey("articles.id", ondelete='CASCADE')), 
    db.Column('tag_id', db.Integer, db.ForeignKey("tags.id", ondelete='CASCADE')),
)


class Category(db.Model):
    """目录"""
    
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), nullable=False)
    longslug = db.Column(db.String(255), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)

    parent_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))
    parent = db.relationship('Category', 
                             primaryjoin = ('Category.parent_id == Category.id'), 
                             remote_side=id, backref=db.backref("children"))

    # SEO page title
    seotitle = db.Column(db.String(128)) 
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255)) 
    template = db.Column(db.String(255)) 
    article_template = db.Column(db.String(255)) 

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [longslug]}

    def __repr__(self):
        return '<Category %r>' % (self.name)

    def __unicode__(self):
        return self.longslug or self.name

    @cached_property
    def link(self):
        return url_for('main.category', longslug=self.longslug, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.category', longslug=self.longslug)

    @cached_property
    def count(self):
        cates = db.session.query(Category.id).filter(Category.longslug.startswith(self.longslug)).all()
        cate_ids = [cate.id for cate in cates]
        return Article.query.public().filter(Article.category_id.in_(cate_ids)).count()

    @cached_property
    def parents(self):
        lst = []
        lst.append(self)
        c = self.parent
        while c is not None:
            lst.append(c)
            c = c.parent
        lst.reverse()
        return lst

    @staticmethod
    def tree():
        """树形列表"""
        cates = Category.query.all()
        out = []
        for cate in cates:
            indent = len(cate.longslug.split('/')) - 1
            out.append((indent, cate))
        return out

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markdown_filter(value)

    def on_changed_longslug(target, value, oldvalue, initiator):
        '''如果栏目有子栏目，则不允许更改longslug，因为会造成longslug不一致'''
        if target.children and value != oldvalue:
            raise Exception('Category has children, longslug can not be change!')

    def gen_longslug(self):
        '''生成longslug'''
        if self.parent:
            _longslug = '/'.join([self.parent.longslug, self.slug]).lower()
        else:
            _longslug = self.slug.lower()
        self.longslug = _longslug

    @staticmethod
    def before_insert(mapper, connection, target):
        target.gen_longslug()

        _c = Category.query.filter_by(longslug=target.longslug).first()
        # 新增时判断longslug是否重复
        if _c:
            raise Exception('Category longslug "%s" already exist' % _c.longslug)

    @staticmethod
    def before_update(mapper, connection, target):
        target.gen_longslug()

        _c = Category.query.filter_by(longslug=target.longslug).first()
        # 更新时判断longslug是否重复
        if _c and _c.id != target.id:
            raise Exception('Category longslug "%s" already exist' % _c.longslug)

db.event.listen(Category.body, 'set', Category.on_changed_body)
db.event.listen(Category.longslug, 'set', Category.on_changed_longslug)
db.event.listen(Category, 'before_insert', Category.before_insert)
db.event.listen(Category, 'before_update', Category.before_update)


class TagQuery(BaseQuery):

    def search(self, keyword):
        keyword = '%' + keyword.strip() + '%'
        return self.filter(Article.title.ilike(keyword))
        
        
class Tag(db.Model):
    """标签"""
    
    __tablename__ = "tags"
    
    query_class = TagQuery

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True, nullable=False)
    
    # SEO info
    seotitle = db.Column(db.String(128))
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255)) 
    template = db.Column(db.String(255)) 

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Tag %r>' % (self.name)

    def __unicode__(self):
        return self.name

    @cached_property
    def link(self):
        return url_for('main.tag', name=self.name.lower(), _external=True)
        
    @cached_property
    def shortlink(self):
        return url_for('main.tag', name=self.name.lower())

    @cached_property
    def count(self):
        return Article.query.public().filter(Article.tags.any(id=self.id)).count()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markdown_filter(value)

db.event.listen(Tag.body, 'set', Tag.on_changed_body)


class Topic(db.Model):
    """专题"""
    
    __tablename__ = "topics"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(64), unique=True, index=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)

    # SEO page title
    seotitle = db.Column(db.String(128)) 
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))

    thumbnail = db.Column(db.String(255)) 
    template = db.Column(db.String(255)) 

    body = db.Column(db.Text)
    body_html = db.Column(db.Text)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Topic %r>' % (self.name)

    def __unicode__(self):
        return self.name

    @cached_property
    def link(self):
        return url_for('main.topic', slug=self.slug, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.topic', slug=self.slug)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markdown_filter(value)

db.event.listen(Topic.body, 'set', Topic.on_changed_body)


class ArticleQuery(BaseQuery):

    def public(self):
        return self.filter_by(published=True)

    def search(self, keywords):
        criteria = []

        for keyword in keywords.split():
            keyword = '%' + keyword + '%'
            criteria.append(db.or_(Article.title.ilike(keyword),))

        q = reduce(db.or_, criteria)
        return self.public().filter(q)

    def archives(self, year, month):
        if not year:
            return self
        
        criteria = []
        criteria.append(db.extract('year', Article.created)==year)
        if month:
            criteria.append(db.extract('month', Article.created)==month)
        
        q = reduce(db.and_, criteria)
        return self.public().filter(q)


class Article(db.Model):
    """贴文"""

    __tablename__ = "articles"

    query_class = ArticleQuery

    PER_PAGE = 10
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)

    seotitle = db.Column(db.String(200))
    seokey = db.Column(db.String(128))
    seodesc = db.Column(db.String(300))
    
    category_id = db.Column(db.Integer(), db.ForeignKey(Category.id), nullable=False,)
    category = db.relationship(Category, backref=db.backref("articles"))

    topic_id = db.Column(db.Integer(), db.ForeignKey(Topic.id))
    topic = db.relationship(Topic, backref=db.backref("articles"))

    tags = db.relationship(Tag, secondary=article_tags_table, backref=db.backref("articles"))

    thumbnail = db.Column(db.String(255))
    thumbnail_big = db.Column(db.String(255))
    template = db.Column(db.String(255)) 

    summary = db.Column(db.String(2000))
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text)

    published = db.Column(db.Boolean, default=False)
    ontop = db.Column(db.Boolean, default=False)
    recommend = db.Column(db.Boolean, default=False)

    hits = db.Column(db.Integer, default=0)

    author_id = db.Column(db.Integer, db.ForeignKey(User.id))
    author = db.relationship(User, backref=db.backref("articles"))

    created = db.Column(db.DateTime())
    last_modified = db.Column(db.DateTime())
    
    __mapper_args__ = {'order_by': [ontop.desc(), id.desc()]}
    
    def __repr__(self):
        return '<Post %r>' % (self.title)

    def __unicode__(self):
        return self.title

    @cached_property
    def has_more(self):
        return self.body.find('<!--more-->') > 0 or (self.summary.find('...') > 0)

    @cached_property
    def link(self):
        return url_for('main.article', article_id=self.id, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.article', article_id=self.id)

    @cached_property
    def get_next(self):
        _query = db.and_(Article.category_id.in_([self.category.id]), 
                         Article.id > self.id)
        return self.query.public().filter(_query) \
                         .order_by(Article.id.asc()) \
                         .first()

    @cached_property
    def get_prev(self):
        _query = db.and_(Article.category_id.in_([self.category.id]), 
                         Article.id < self.id)
        return self.query.public().filter(_query) \
                         .order_by(Article.id.desc()) \
                         .first()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        def _format(_html):
            return truncate(remove_formatting(_html), length=200, whole_word=True)

        if BODY_FORMAT == 'html':
            target.body_html = value
            target.summary = _format(value)
        else:
            target.body_html = markdown_filter(value)
            more_start = value.find('<!--more-->')
            if more_start > 0:
                target.summary = _format(markdown_filter(value[:more_start]))
            else:
                target.summary = _format(target.body_html)

db.event.listen(Article.body, 'set', Article.on_changed_body)


class Link(db.Model):
    """内部链接"""

    __tablename__ = 'links'

    id = db.Column(db.Integer, primary_key=True)
    anchor = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128))
    url = db.Column(db.String(255), nullable=False)
    note = db.Column(db.String(200))

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Link %r>' % (self.anchor)

    def __unicode__(self):
        return self.anchor


class FriendLink(db.Model):
    """友情链接"""

    __tablename__ = 'friendlinks'

    id = db.Column(db.Integer, primary_key=True)
    anchor = db.Column(db.String(64), nullable=False)
    title = db.Column(db.String(128))
    url = db.Column(db.String(255), nullable=False)
    actived = db.Column(db.Boolean, default=False)
    note = db.Column(db.String(400))

    __mapper_args__ = {'order_by': [actived.desc(), id.desc()]}

    def __repr__(self):
        return '<FriendLink %r>' % (self.anchor)

    def __unicode__(self):
        return self.anchor


class Flatpage(db.Model):
    """单页面"""

    __tablename__ = 'flatpages'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Unicode(100), nullable=False, )
    seotitle = db.Column(db.Unicode(200))
    seokey = db.Column(db.Unicode(128))
    seodesc = db.Column(db.Unicode(400))
    template = db.Column(db.String(255)) 
    body = db.Column(db.Text, nullable=False)
    body_html = db.Column(db.Text, nullable=False)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Flatpage %r>' % (self.title)

    def __unicode__(self):
        return self.title

    @cached_property
    def link(self):
        return url_for('main.flatpage', slug=self.slug, _external=True)

    @cached_property
    def shortlink(self):
        return url_for('main.flatpage', slug=self.slug)

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        if BODY_FORMAT == 'html':
            target.body_html = value
        else:
            target.body_html = markdown_filter(value)

db.event.listen(Flatpage.body, 'set', Flatpage.on_changed_body)


class Label(db.Model):
    """HTML代码片断"""

    __tablename__ = 'labels'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(32), nullable=False)
    title = db.Column(db.Unicode(100), nullable=False, )
    html = db.Column(db.Text, nullable=False)

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Label %r>' % (self.title)

    def __unicode__(self):
        return self.title


class Redirect(db.Model):
    """重定向"""

    __tablename__ = 'redirects'

    id = db.Column(db.Integer, primary_key=True)
    old_path = db.Column(db.String(128), nullable=False)
    new_path = db.Column(db.String(128), nullable=False)
    note = db.Column(db.String(400))

    __mapper_args__ = {'order_by': [id.desc()]}

    def __repr__(self):
        return '<Redirect %r>' % (self.old_path)

    def __unicode__(self):
        return self.old_path


