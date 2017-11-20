# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import sessionmaker
#
# from ..base import app
#
# engine = create_engine(app.config['DSN'], echo=app.config['SQLALCHEMY_ECHO'])
#
# DBSession = scoped_session(sessionmaker(bind=engine))
# session = DBSession()


from ..base import db

Model = db.Model
session = db.session

from user import *