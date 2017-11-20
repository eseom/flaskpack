# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

import flask_login
from flask_admin.contrib import sqla


class ModelView(sqla.ModelView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated
