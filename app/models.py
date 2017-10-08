from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

from app import db
from flask import current_app as app

__author__ = 'Ankit Joshi'


class Admin(db.Model):
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        admin = Admin.query.get(data['id'])
        return admin

    def __repr__(self):
        return '<Admin: {}>'.format(self.name)


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.String(7), index=True)
    name = db.Column(db.String(32), index=True)
    email = db.Column(db.String(128))
    year = db.Column(db.Integer)
    phoneno = db.Column(db.String(10))
    section = db.Column(db.Integer)
    branch = db.Column(db.Integer)
    base64_image = db.Column(db.Text)

    def __repr__(self):
        return '<Student: {}>'.format(self.name)
