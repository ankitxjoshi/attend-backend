from flask import abort, request, jsonify, g, url_for
from flask_cors import CORS, cross_origin
import os

from . import admin
from .. import db
from ..models import Admin, Student
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


@admin.route('/store', methods=['POST'])
def new_student_entry():
    name = request.get_json()['name']
    rollno = request.get_json()['rollno']
    email = request.get_json()['email']
    phoneno = request.get_json()['phoneno']
    year = int(request.get_json()['year'])
    branch = int(request.get_json()['branch'])
    section = int(request.get_json()['section'])
    base64_image = request.get_json()['base64Image']

    student_data = [name, rollno, email, phoneno, year, branch, section, base64_image]

    # missing arguments
    for data in student_data:
        if data is None:
            return jsonify(
                status=const.status['BAD_REQUEST'],
                message=const.string['MISSING_ARGS']
            )

    # existing student
    if Student.query.filter_by(rollno=rollno).first() is not None:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_EXISTS']
        )

    student = Student(name=name,
                      email=email,
                      rollno=rollno,
                      phoneno=phoneno,
                      year=year,
                      branch=branch,
                      section=section,
                      base64_image=base64_image)

    db.session.add(student)
    db.session.commit()

    new_student_directory = const.openface['RAW_DIR'] + '/' + rollno
    try:
        if not os.path.exists(new_student_directory):
            os.makedirs(new_student_directory)
        image_path = new_student_directory + '/' + name + '.png'
        with open(image_path, "wb") as fh:
            fh.write(base64_image.decode('base64'))
    except:
        return jsonify(
            status=const.status['INTERNAL_SERVER_ERROR'],
            message=const.string['SERVER_ERROR']
        )

    return jsonify(
        student=student.rollno,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )
