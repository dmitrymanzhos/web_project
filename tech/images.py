import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash
from .db_session import SQLAlchemyBase
from sqlalchemy_serializer import SerializerMixin
import datetime


class Image(SQLAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'images'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    filepath = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    user = orm.relationship('User')
