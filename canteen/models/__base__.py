# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

from datetime import datetime

from sqlalchemy import Column, Integer, DateTime


# from . import DBSession

# Base = declarative_base()
# Base.query = DBSession.query_property()


class BaseMixin(object):
    id = Column(Integer, primary_key=True)
    created_at = Column('created_at', DateTime, nullable=False,
                        default=datetime.now)
    updated_at = Column('updated_at', DateTime, nullable=False,
                        default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return '<{self.__class__.__name__}:{self.id}>'.format(self=self)
