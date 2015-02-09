# -*- coding: utf-8 -*-

import os
import sys
from os import path

deps_paths = [
    path.join(path.split(path.realpath(__file__))[0], 'deps'),
    path.join(path.split(path.realpath(__file__))[0], 'mydeps'),
]

for deps_path in deps_paths:
    if deps_path not in sys.path:
        sys.path.insert(0, deps_path)

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='wtxlog/*')
    COV.start()

from wtxlog import create_app, db, get_appconfig
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# bae, sae, production, local(default)
app = create_app(os.getenv('APP_CONFIG') or str(get_appconfig()) or 'default')

manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    from wtxlog.models import Role

    upgrade()
    # db.create_all()

    # create user roles
    Role.insert_roles()


@manager.shell
def make_shell_context():
    from wtxlog.models import User, Role, Permission, Category, Tag, \
        Article, Topic, Link, FriendLink, Flatpage, Label, Redirect, Setting
    return dict(
        app=app, db=db, User=User, Role=Role, Permission=Permission,
        Category=Category, Tag=Tag, Article=Article, Topic=Topic,
        Link=Link, FriendLink=FriendLink, Flatpage=Flatpage,
        Label=Label, Redirect=Redirect, Setting=Setting
    )


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp', 'coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()
