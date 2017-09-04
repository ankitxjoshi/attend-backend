from flask import abort, request, jsonify, g, url_for

from . import admin
from .. import db
from ..models import Admin
from ..decorators import auth
import constants as const

__author__ = 'Ankit Joshi'


@admin.route('/create', methods=['POST'])
def new_admin():
    username = request.json.get('username')
    password = request.json.get('password')

    # missing arguments
    if username is None or password is None:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['MISSING_ARGS']
        )

    # existing admin
    if Admin.query.filter_by(username=username).first() is not None:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_EXISTS']
        )

    admin = Admin(username=username)
    admin.hash_password(password)
    db.session.add(admin)
    db.session.commit()

    return jsonify(
        username=admin.username,
        location=url_for('get_admin', id=admin.id, _external=True),
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@admin.route('/<int:id>')
def get_admin(id):
    admin = Admin.query.get(id)
    if not admin:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    return jsonify(
        username=admin.username,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@admin.route('/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.admin.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})
