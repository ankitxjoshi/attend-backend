import os

from flask import request, jsonify, g, url_for

import constants as const
from . import admin
from .. import db
from ..decorators import auth
from ..models import Admin, Student

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
        location=url_for('.get_admin', id=admin.id, _external=True),
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


# TODO: Remove comment after implementing login
# @auth.login_required
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

    # Storing profile image
    new_student_directory = const.openface['RAW_DIR'] + '/' + rollno
    image_path = new_student_directory + '/' + name + '.png'
    try:
        if not os.path.exists(new_student_directory):
            os.makedirs(new_student_directory)
        with open(image_path, "wb") as fh:
            fh.write(base64_image.decode('base64'))
    except:
        return jsonify(
            status=const.status['INTERNAL_SERVER_ERROR'],
            message=const.string['SERVER_ERROR']
        )

    try:
        student = Student(name=name,
                          email=email,
                          rollno=rollno,
                          phoneno=phoneno,
                          year=year,
                          branch=branch,
                          section=section,
                          password_hash=rollno,
                          image_url=image_path)
        student.hash_password(rollno)

        db.session.add(student)
        db.session.commit()
    except:
        return jsonify(
            status=const.status['INTERNAL_SERVER_ERROR'],
            message=const.string['BAD_INPUT']
        )

    return jsonify(
        student=student.rollno,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@admin.route('/student/<path:rollno>')
def get_student(rollno):
    student = Student.query.filter_by(rollno=rollno).first()
    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    data = [student.name, student.rollno, student.email,
            student.phoneno, student.year, student.branch,
            student.section]

    return jsonify(
        data=data,
        image_path=student.image_url,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@admin.route('/student')
def get_students():
    students = Student.query.all()
    students_rollno = [student.rollno for student in students]
    print '-' * 100
    print students_rollno
    return jsonify(
        data=students_rollno,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )
