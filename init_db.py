# -*- coding: utf-8 -*-

"""
Just for development time
"""

from manage import db
from wtxlog.models import User, Role, Category

if __name__ == '__main__':
    # init database
    db.create_all()

    # create user roles
    Role.insert_roles()

    # add administrator
    user = User()
    user.username = 'admin'
    user.password = 'admin'
    user.email = 'admin@example.com'
    user.role = Role.query.filter_by(permissions=0xff).first()
    user.confirmed = True

    # add default category
    category = Category()
    category.slug = 'default'
    category.name = 'Default'

    # commit
    db.session.add(user)
    db.session.add(category)
    db.session.commit()

    print('==================================')
    print('Init Done.')
    print('==================================')
