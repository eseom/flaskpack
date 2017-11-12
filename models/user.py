# coding: utf-8

"""
"""

from __future__ import unicode_literals, print_function

from datetime import datetime

from flask_security import RoleMixin, UserMixin
from flask_security.utils import hash_password
from sqlalchemy import Column, Integer, Unicode, UnicodeText, Boolean, \
    DateTime, String, Table, Date, CHAR, UniqueConstraint
from sqlalchemy import ForeignKey, and_
from sqlalchemy.orm import backref, relationship, synonym

from . import session
from .__base__ import Base, BaseMixin

roles_users = Table(
    'roles_users',
    Base.metadata,
    Column('user_id', Integer(), ForeignKey('users.id')),
    Column('role_id', Integer(), ForeignKey('roles.id')))


def get_or_create(session, model, **kwargs):
    """
    Creates an object or returns the object if exists
    credit to Kevin @ StackOverflow
    from: http://stackoverflow.com/questions/2546207/does-sqlalchemy-have-an-equivalent-of-djangos-get-or-create
    """

    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


class Role(Base, RoleMixin):
    __tablename__ = 'roles'

    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    def __repr__(self):
        return '<{self.__class__.__name__}:{self.name}>'.format(self=self)


class User(Base, UserMixin):
    __tablename__ = 'users'

    obj_type = 'User'

    id = Column(Integer, primary_key=True)
    email = Column(Unicode(255), unique=True)
    username = Column(Unicode(20), unique=True)
    dob = Column(Date)
    gender = Column(CHAR(1))
    password = Column(String(255))
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary=roles_users,
                         backref=backref('users', lazy='dynamic'))

    current_login_at = Column(DateTime())
    current_login_ip = Column(String(255))
    login_count = Column(Integer)

    # extra info

    metainfo = relationship('UserMeta', backref='user', uselist=False, )

    def get_metainfo(self):
        return self.metainfo

    def get_metainfo_model(self):
        return UserMeta

    # @property
    # def profile_url(self):
    #     media = Media.query.filter_by(obj_type=self.obj_type,
    #                                   obj_id=self.id).order_by(
    #         Media.updated_at.desc()).first()
    #     if media:
    #         return media.media_url_sa

    # @property
    # def thumbnail_url(self):
    #     media = Media.query.filter_by(obj_type=self.obj_type,
    #                                   obj_id=self.id).order_by(
    #         Media.updated_at.desc()).first()
    #     if media:
    #         return media.thumbnail_url_sa

    @property
    def has_admin_privs(self):
        for role in self.roles:
            if role.name.lower() == 'admin':
                return True

        return False

    @classmethod
    def get_by_id_or_username(cls, id_or_username):
        if str(id_or_username).isdigit():
            return cls.query.get(int(id_or_username))
        else:
            return cls.query.filter_by(username=(id_or_username)).first()

    def get_incoming_status(self, user_id):
        """
        현재 사용자를 (user_id에 해당하는) 타겟사용자가 follow 하는지 여부를 확인.

        A user's relationship to you. Can be 'followed_by', 'requested_by',
        'blocked_by_you', 'none'.

        follow 하는 경우 'followed_by', 아닌 경우 None 을 리턴
        """
        rel = Relationship.query.filter_by(user_id=self.id,
                                           followed_by_id=user_id).first()
        if rel:
            return 'followed_by'

    def get_outgoing_status(self, user_id):
        """
        현재 사용자가 (user_id에 해당하는) 타겟사용자를 follow 하는지 여부를 확인.

        Your relationship to the user. Can be 'follows', 'requested', 'none'.

        follow 하는 경우 'follow', 아닌 경우 None 을 리턴
        """
        rel = Relationship.query.filter_by(user_id=user_id,
                                           followed_by_id=self.id).first()

        if rel:
            return 'follows'

    @classmethod
    def createuser(self, session, email, password, roles=None):
        user = User(email=email, active=True, confirmed_at=datetime.now())
        user.set_password(password)

        if roles:
            user.roles = roles

        session.add(user)
        return user

    def update_follows_count(self):
        metainfo_model = self.get_metainfo_model()
        metainfo = get_or_create(session, metainfo_model, obj_id=self.id)
        metainfo.cnt_follows = Relationship.query.join(
            User, and_(Relationship.user_id == User.id, User.active == True)
        ).filter(
            Relationship.followed_by_id == self.id
        ).count()

        return metainfo

    def update_followed_by_count(self):
        metainfo_model = self.get_metainfo_model()
        metainfo = get_or_create(session, metainfo_model, obj_id=self.id)
        metainfo.cnt_followed_by = Relationship.query.join(
            User,
            and_(Relationship.followed_by_id == User.id, User.active == True)
        ).filter(
            Relationship.user_id == self.id
        ).count()

        return metainfo

    def set_password(self, password):
        self.password = hash_password(password)

    def __repr__(self):
        return '<{self.__class__.__name__}:{self.email}>'.format(self=self)


class UserMeta(Base, BaseMixin):
    __tablename__ = 'user_meta'

    obj_id = Column(Integer, ForeignKey(User.id), nullable=False, )

    cnt_follows = Column(Integer, default=0)
    cnt_followed_by = Column(Integer, default=0)


class Relationship(Base, BaseMixin):
    __tablename__ = 'relationships'
    __table_args__ = (
        (UniqueConstraint("user_id", "followed_by_id",
                          name="unique_idx_user_id_followed_by_id")),
    )

    user_id = Column(Integer, ForeignKey('users.id'))
    followed_by_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', foreign_keys=user_id, backref='followed_by')
    followed_by = relationship('User', foreign_keys=followed_by_id,
                               backref='follows')

    def __init__(self, user_id=None, followed_by_id=None):
        self.user_id = user_id
        self.followed_by_id = followed_by_id

    def __repr__(self):
        return '<{self.__class__.__name__}: {self.followed_by_id} to ' \
               '{self.user_id}>'.format(self=self)


class DeviceToken(Base, BaseMixin):
    __tablename__ = 'device_tokens'

    user_id = Column(Integer, ForeignKey('users.id'))
    token = Column(Unicode)

    user = relationship('User', foreign_keys=user_id, backref='device_token')


class Client(Base):
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


class Grant(Base):
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


class Token(Base):
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
