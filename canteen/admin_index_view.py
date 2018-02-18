import flask_login
from flask_admin import AdminIndexView as FlaskAdminIndexView, expose


class AdminIndexView(FlaskAdminIndexView):
    def is_accessible(self):
        return flask_login.current_user.is_authenticated

    # def _handle_view(self, name, *args, **kwargs):
    #     if not current_user.is_authenticated:
    #         return redirect(url_for_security('login', next="/admin"))

    @expose('/')
    def index(self):
        return super(AdminIndexView, self).index()
