# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

import base
import yaml
from flask import Flask, Blueprint, jsonify
from flask_admin import Admin
from flask_collect import Collect
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_security import SQLAlchemySessionUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy


class FlaskWrapper(Flask):
    def __init__(self):
        """
        app
        """
        Flask.__init__(self, __name__, template_folder='templates')
        base.app = self

        self.config.from_envvar('SETTINGS')
        self.secret_key = 'super secret key'

        """
        cors
        """
        CORS(self, resources={
            r"/api/*": {"origins": "*"},
            r"/spec": {"origins": "*"},
        })

        """
        collect
        """
        Collect(base.app)

        """
        sqlalchemy
        """
        base.db = SQLAlchemy(base.app)

        """
        migrate
        """

        Migrate(base.app, base.db)

        """
        DebugToolbar
        """
        if base.app.config.get('DEBUG', False):
            DebugToolbarExtension(base.app)

        """
        admin
        """
        from .admin_index_view import AdminIndexView

        base_url = self.config.get('FLASK_ADMIN_URL', '/admin')
        base.admin = Admin(
            self,
            url=base_url,
            name=self.config.get('APPNAME', 'flask app'),
            template_mode='bootstrap3',
            base_template='admin/base_.html',
            index_view=AdminIndexView(url=base_url),
        )

        """
        swagger
        """
        from .swagger import get_swaggerui_blueprint
        from flask_swagger import swagger

        SWAGGER_URL = self.config.get('SWAGGER_URL', '/api/docs')
        API_URL = '/spec'

        swaggerui_blueprint = get_swaggerui_blueprint(
            SWAGGER_URL,
            API_URL,
            config={  # Swagger UI config overrides
                'app_name': '%s API' % self.config.get('APPNAME', 'flask app'),
            },
            oauth_config={
                'clientId': "swagger",
            }
        )

        self.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

        @self.route("/spec")
        def spec():
            swag = swagger(self)
            swag_from_file = yaml.load(open('./swagger/spec.yaml'))
            swag.update(swag_from_file)
            return jsonify(swag)

        """
        internal blueprint
        """
        base.internal_bp = Blueprint('internal', 'internal_bp')

        """
        oauth
        """
        from flask_oauthlib.provider import OAuth2Provider

        base.oauth = OAuth2Provider(self)
        import oauth

        """
        flask login
        """
        from .models import session, User, Role

        user_datastore = SQLAlchemySessionUserDatastore(session, User, Role)
        security = Security(self, user_datastore)

        """
        modules
        """
        import views
        import admins

        self.register_blueprint(base.internal_bp)


app = FlaskWrapper()
