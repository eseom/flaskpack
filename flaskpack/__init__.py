import jinja2
import yaml
from flask import *
from flask_admin import Admin
from flask_collect import Collect
from flask_cors import CORS
from flask_debugtoolbar import DebugToolbarExtension
from flask_migrate import Migrate
from flask_security import SQLAlchemySessionUserDatastore, Security
from flask_sqlalchemy import SQLAlchemy

from . import base


class Flaskpack(Flask):
    def __init__(self, root_path, template_folders, **kwargs):
        """
        work with Flask constructor args
        """
        AdminIndexView = kwargs.get('admin_index_view', None)
        try:
            del kwargs['admin_index_view']
        except:
            pass

        """
        app
        """
        Flask.__init__(self, __name__, **kwargs)
        base.app = self
        base.app.root_path = root_path

        self.config.from_envvar('SETTINGS')
        self.secret_key = 'super secret key'

        """
        set custom jinja loader
        """
        tfs = [base.app.jinja_loader]
        for tf in template_folders:
            tfs.append(jinja2.FileSystemLoader(tf))
        loader = jinja2.ChoiceLoader(tfs)
        base.app.jinja_loader = loader

        """
        cors
        """
        CORS(self, resources={
            r"/v2/*": {"origins": "*"},
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
        if not AdminIndexView:
            from .admin_index_view import AdminIndexView

        base_url = self.config.get('FLASK_ADMIN_URL', '/admin')
        base.admin = Admin(
            self,
            url=base_url,
            name=self.config.get('APPNAME', 'flask app'),
            template_mode='bootstrap3',
            base_template=self.config.get('FLASK_ADMIN_BASE_TEMPLATE',
                                          'admin/base_.html'),
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
            swag_from_file = yaml.load(open(base.app.root_path + '/../swagger/spec.yaml'))
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
        from . import oauth

        """
        flask login
        """
        from .models import session, User, Role

        user_datastore = SQLAlchemySessionUserDatastore(session, User, Role)
        security = Security(self, user_datastore)

        """
        modules
        """
        from . import views, admins

        self.register_blueprint(
            base.internal_bp,
            url_prefix=base.app.config.get('CANTEEN_URL_PREFIX', '')
        )


app = None


def init(**kwargs):
    import inspect
    import os
    import sys

    # reset root path
    if sys.version_info.major == 3:
        root_path = os.path.dirname(
            os.path.abspath(inspect.stack()[1].filename))
    else:
        root_path = os.path.dirname(os.path.abspath(inspect.stack()[1][1]))

    # template folders
    flaskpack_template_path = '%s/templates' % os.path.dirname(__file__)
    template_folders = []
    tp = kwargs.get('template_folder')
    if type(tp) == 'list':
        template_folders.append(flaskpack_template_path)
    elif type(tp) == 'str':
        template_folders = [flaskpack_template_path, tp]
    else:
        template_folders = [
            '%s/templates' % root_path,
            flaskpack_template_path,
        ]

    global app
    if not app:
        app = Flaskpack(root_path, template_folders, **kwargs)
    return app

