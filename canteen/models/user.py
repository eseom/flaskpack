# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

from datetime import datetime

from flask_security import RoleMixin, UserMixin
from sqlalchemy import Column, Integer, Unicode, UnicodeText, Boolean, \
    DateTime
from sqlalchemy.orm import synonym

from .__base__ import BaseMixin
from ..base import db

Model = db.Model
session = db.session

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship

admin_users = db.Table('admin_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('users.id')),
                       db.Column('admin_id', db.Integer(),
                                 db.ForeignKey('admins.id')))

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('users.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('roles.id')))


class Admin(Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    metainfo = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<{self.name}>'.format(self=self)


class Role(Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    metainfo = db.Column(db.UnicodeText)

    def __repr__(self):
        return '<Role {self.name}>'.format(self=self)


class User(Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(20), unique=True)
    dob = db.Column(db.Date)
    gender = db.Column(db.CHAR(1))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    current_login_at = db.Column(db.DateTime())
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer)

    im_user_type = db.Column(db.Integer)  # None, Fixed
    im_max_account = db.Column(db.Integer)
    im_expire_at = db.Column(db.DateTime())

    kg_user_type = db.Column(db.Integer)  # None, Fixed, Point
    kg_max_account = db.Column(db.Integer)
    kg_expire_at = db.Column(db.DateTime())

    # 설정
    email_upload_success = db.Column(db.Boolean,
                                     default=True)  # 업로드 성공시 메일알림 받기
    email_upload_error = db.Column(db.Boolean, default=True)  # 업로드 실패시 메일알림 받기

    memo_text = db.Column(db.UnicodeText())

    is_agency = db.Column(db.Boolean(), default=False)
    is_deleted = db.Column(db.Boolean(), default=False)  # 삭제 처리

    created_by_user_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    created_by_user = relationship('Admin', foreign_keys=created_by_user_id, )

    manager_id = db.Column(db.Integer, db.ForeignKey('admins.id'))
    manager = relationship('Admin', foreign_keys=manager_id)

    @property
    def num_accounts(self):
        return len(self.accounts)

    @property
    def lab_enabled(self):
        return self.has_role('lab')

    @property
    def point_available(self):
        if self.point_info:
            return self.point_info.point_available

        return 0

    # @property
    # def im_user(self):
    #     expire_at = None
    #     if self.im_expire_at:
    #         expire_at = self.im_expire_at.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    #
    #     active_accounts = Account.query.filter(Account.user == self, Account.im_active == True).count()
    #
    #     return {
    #         'max_account': self.im_max_account,
    #         'type': (IM_USER_TYPE.reverse_mapping.get(self.im_user_type)),
    #         'expire_at': expire_at,
    #         'active_accounts': active_accounts,
    #     }

    # @property
    # def im_ready(self):
    #     """
    #     사용자 설정 기준으로 인스타매니저 사용 가능 여부 체크
    #
    #     :return:
    #     """
    #     # USER_IM_TYPE == FIXED
    #     if self.im_user_type not in (IM_USER_TYPE.FIXED_MONTHLY,):
    #         current_app.logger.info('NOT_IM_READY: IM_USER_TYPE: %s' % self.im_user_type)
    #         return False
    #
    #     # USER.IM_NOT_EXPIRED
    #     if self.im_expire_at and self.im_expire_at < datetime.now():
    #         current_app.logger.info('NOT_IM_READY: IM_EXPIRE_AT: %s' % self.im_expire_at)
    #         return False
    #
    #     return True

    # @property
    # def kg_user(self):
    #     expire_at = None
    #     if self.kg_expire_at:
    #         expire_at = self.kg_expire_at.strftime('%Y-%m-%dT%H:%M:%S+09:00')
    #
    #     active_accounts = Account.query.filter(Account.user == self, Account.kg_active == True).count()
    #
    #     return {
    #         'max_account': self.kg_max_account,
    #         'type': (KG_USER_TYPE.reverse_mapping.get(self.kg_user_type)),
    #         'expire_at': expire_at,
    #         'active_accounts': active_accounts,
    #     }

    # @property
    # def kg_ready(self):
    #     """
    #     사용자 설정 기준으로 일킬로그램 사용 가능 여부 체크
    #
    #     :return:
    #     """
    #     # USER_KG_TYPE == FIXED, POINT
    #     if self.kg_user_type not in (KG_USER_TYPE.FIXED_MONTHLY, KG_USER_TYPE.POINT, ):
    #         current_app.logger.info('NOT_KG_READY: KG_USER_TYPE: %s' % self.kg_user_type)
    #         return False
    #
    #     # USER.KG_NOT_EXPIRED
    #     if self.kg_expire_at and self.kg_expire_at < datetime.now():
    #         current_app.logger.info('NOT_KG_READY: KG_EXPIRE_AT: %s' % self.kg_expire_at)
    #         return False
    #
    #     return True

    @property
    def settings(self):
        return {
            'email_upload_error': self.email_upload_error,
            'email_upload_success': self.email_upload_success,
        }

    @property
    def access_token(self):
        return db.session.query(Token).filter(
            Token.user == self,
            Token.expires > datetime.now(),
        ).first()

    @property
    def access_tokens(self):
        return db.session.query(Token).filter(Token.user == self).all()

    def __repr__(self):
        return '<{self.email}>'.format(self=self)


class Relationship(Model, BaseMixin):
    __tablename__ = 'relationships'
    __table_args__ = (
        (UniqueConstraint("user_id", "followed_by_id",
                          name="unique_idx_user_id_followed_by_id")),
    )

    user_id = db.Column(db.Integer, ForeignKey('users.id'))
    followed_by_id = db.Column(db.Integer, ForeignKey('users.id'))

    user = relationship('User', foreign_keys=user_id, backref='followed_by')
    followed_by = relationship('User', foreign_keys=followed_by_id,
                               backref='follows')

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.followed_by_id} to {self.user_id}>'.format(
            self=self)


class Client(Model):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(40))

    # human readable description, not required
    description = Column(Unicode(400))

    # creator of the client, not required
    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
    )
    user = relationship('User')

    client_id = Column(Unicode(40), unique=True)
    client_secret = Column(Unicode(55), index=True, nullable=False)

    # public or confidential
    is_confidential = Column(Boolean)

    redirect_uris_text = Column(UnicodeText)
    default_scopes_text = Column(UnicodeText)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self.redirect_uris_text:
            return self.redirect_uris_text.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self.default_scopes_text:
            return self.default_scopes_text.split()
        return []

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)


class Grant(Model):
    __tablename__ = 'grants'

    id = Column(Integer, primary_key=True)

    # user_id = Column(Unicode(200))dd
    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
    )
    user = relationship('User')

    client_id = Column(
        Unicode(40),
        ForeignKey('clients.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    code = Column(Unicode(255), index=True, nullable=False)

    redirect_uri = Column(Unicode(255))
    expires = Column(DateTime)

    _scopes = Column(UnicodeText)

    def delete(self):
        session.delete(self)
        session.commit()
        return self

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []


class Token(Model):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    client_id = Column(
        Unicode(40),
        ForeignKey('clients.client_id'),
        nullable=False,
    )
    client = relationship('Client')

    user_id = Column(
        Integer,
        ForeignKey('users.id'),
        nullable=False,
    )
    user = relationship('User')

    # currently only bearer is supported
    token_type = Column(Unicode(40))

    access_token = Column(Unicode(255), unique=True)
    refresh_token = Column(Unicode(255), unique=True)
    expires = Column(DateTime)
    _scopes = Column(UnicodeText)

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def _get_scope(self):
        if self._scopes:
            return self._scopes.split()
        return []

    def _set_scope(self, scope):
        if scope:
            scope = scope
        self._scopes = scope

    scope_descriptor = property(_get_scope, _set_scope)
    scope = synonym('_scopes', descriptor=scope_descriptor)

    def __repr__(self):
        return u'<{self.__class__.__name__}: {self.id}>'.format(self=self)
