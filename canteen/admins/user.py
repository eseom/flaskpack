# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

from .__base__ import MyModelView
from ..base import admin
from ..models import User, Role, Client, Token, session

admin.add_view(MyModelView(User, session, category='User'))
admin.add_view(MyModelView(Role, session, category='User'))
admin.add_view(MyModelView(Client, session, category='User'))
admin.add_view(MyModelView(Token, session, category='User'))
