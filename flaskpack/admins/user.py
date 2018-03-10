from .__base__ import ModelView
from ..base import admin
from ..models import User, Role, Client, Grant, Token, session

admin.add_view(ModelView(User, session, category='System'))
admin.add_view(ModelView(Role, session, category='System'))
admin.add_view(ModelView(Grant, session, category='System'))
admin.add_view(ModelView(Client, session, category='System'))
admin.add_view(ModelView(Token, session, category='System'))
