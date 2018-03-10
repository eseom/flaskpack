from datetime import datetime, timedelta

from flask import request, render_template, redirect, jsonify
from flask_login import current_user, login_required
from flask_security.utils import verify_password

from .base import oauth, internal_bp
from .models import session, User, Client, Grant, Token


@oauth.clientgetter
def load_user_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()


@oauth.grantgetter
def load_user_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()


def get_current_user():
    return session.query(User).get(current_user.id)


@oauth.grantsetter
def save_user_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        redirect_uri=request.redirect_uri,
        _scopes=' '.join(request.scopes),
        user_id=get_current_user().id,
        expires=expires
    )
    session.add(grant)
    session.commit()
    return grant


@oauth.tokengetter
def load_user_token(access_token=None, refresh_token=None):
    if access_token:
        tok = Token.query.filter_by(access_token=access_token).first()
        if tok and tok.user_id:
            tok.user = User.query.get(tok.user_id)
        return tok
    elif refresh_token:
        tok = Token.query.filter_by(refresh_token=refresh_token).first()
        if tok and tok.user_id:
            tok.user = User.query.get(tok.user_id)
        return tok


@oauth.tokensetter
def save_user_token(token, request, *args, **kwargs):
    expires_in = token.pop('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    token_data = {key: token[key] for key in token.keys()
                  if key in (
                      'token_type', 'scope', 'access_token', 'refresh_token')}
    tok = Token(**token_data)
    tok.expires = expires
    tok.client_id = request.client.client_id

    if not request.user:
        tok.user_id = current_user.id
    else:
        tok.user_id = request.user.id

    session.add(tok)
    session.commit()
    return tok


@oauth.usergetter
def get_user(email, password, *args, **kwargs):
    user = User.query.filter_by(email=email).first()
    # password가 맞고 confirmed_at이 null이 아님
    if (user and verify_password(password, user.password)
        and user.confirmed_at is not None):
        return user
    return None


@oauth.invalid_response
def invalid_require_oauth(req):
    resp = jsonify({
        'message': req.error_message,
    })
    resp.status_code = 401
    return resp


@internal_bp.route('/oauth/authorize', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def user_authorize(*args, **kwargs):
    user = get_current_user()
    if not user:
        return redirect('/')

    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        kwargs['user'] = user
        return render_template('authorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'


@internal_bp.route('/oauth/token', methods=['GET', 'POST'])
@oauth.token_handler
def user_access_token():
    """
    로그인
    ---
    tags:
      - user
    parameters:
      - name: grant_type
        in: query
        description:
        type: string
      - name: client_id
        in: query
        description:
        type: string
      - name: client_secret
        in: query
        description:
        type: string
      - name: username
        in: query
        description:
        type: string
      - name: password
        in: query
        description:
        type: string
      - name: scope
        in: query
        description:
        type: string
    responses:
      200:
        description: OK
        schema:
          $ref: '#/definitions/CommonResult'

    """
    return None


@internal_bp.route('/oauth/revoke')
@oauth.require_oauth('email')
def revoke():
    """
    현재 인증된 access_token 파기
    ---
    tags:
      - user
    security:
      - oauth:
        - email
    responses:
      200:
        description: OK
        schema:
          $ref: '#/definitions/CommonResult'

    """
    if 'Authorization' in request.headers:
        access_token = request.headers.get('Authorization')[7:]
        token = Token.query.filter_by(access_token=access_token).first()
        if token:
            session.delete(token)
            session.commit()

    return jsonify({'result': 'ok'})
