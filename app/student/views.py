import datetime
import json

from flask import jsonify
from sqlalchemy import *

import constants as const
from . import student
from .. import db
from ..models import Student, TimeTable, Period, Classroom, Staff, Attendance

__author__ = 'Shivam Sharma'


# write the routes below
@student.route('/classesOfDay/<string:rollno>', methods=['GET'])
def get_classes_of_day(rollno):
    # get the section and year
    student_details = Student.query.filter_by(rollno=rollno).first()
    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )
    print "Student Details ", student_details.section, student_details.year
    section, year = student_details.section, student_details.year

    now = datetime.datetime.now()
    day = now.strftime("%A")

    time_table_details = (db.session.query(
        TimeTable.subject.label("subject"),
        TimeTable.location.label("classroom"),
        Staff.name.label("faculty_name"),
        Period.start_time.label("begin_time"),
        Period.end_time.label("end_time"),
        Classroom.bluetooth_address.label("bluetooth_address"))
                          .join(Period)
                          .join(Staff)
                          .join(Classroom)
                          .filter(and_(TimeTable.day == day, TimeTable.section == section, TimeTable.year == year))
                          ).all()

    timetable = [dict((name, getattr(x, name)) for name in ['subject', 'classroom', 'faculty_name',
                                                            'begin_time', 'end_time', 'bluetooth_address']) for x in
                 time_table_details]

    if not timetable:
        return jsonify(
            status=const.status['OK'],
            message=const.string['NO_CLASS'])

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = timetable
    return json.dumps(result, indent=4, default=str)


@student.route('/details/<string:rollno>', methods=['GET'])
def get_student_details(rollno):
    student = Student.query.filter_by(rollno=rollno).first()
    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    print "Student details", dir(student)
    data = dict((name, getattr(student, name)) for name in ['branch', 'email', 'id',
                                                            'name', 'phoneno', 'rollno', 'section', 'year'])
    print 'data--------------', data
    return jsonify(
        data=data,
        image_path=student.image_url,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@student.route('/attendance_details_for_subject/<string:rollno>/<string:subject>', methods=['GET'])
def get_attendance_details_for_subject(rollno, subject):
    attendance_details = (db.session.query(
        Attendance.date.label("date"),
        Attendance.presence_flag.label("presence_flag"),
        Attendance.period_id.label("period"),
        Period.start_time.label("begin_time"),
        Period.end_time.label("end_time"))
                          .join(Period)
                          .filter(and_(Attendance.subject == subject, Attendance.rollno == rollno))
                          ).all()

    if not attendance_details:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    attendance = [dict((name, getattr(x, name)) for name in ['date', 'period',
                                                             'presence_flag', 'begin_time', 'end_time']) for x in
                  attendance_details]

    print "time table ---------", attendance[1]

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = attendance
    return json.dumps(result, indent=4, default=str)


@student.route('/attendance_summary_for_subject/<string:rollno>/<string:subject>', methods=['GET'])
def get_attendance_summary_for_subject(rollno, subject):
    total_present = (db.session.query(func.count(Attendance.id))
                     .filter(and_(Attendance.presence_flag is True,
                                  Attendance.subject == subject,
                                  Attendance.rollno == rollno))).first()[0]

    total_attendance = (db.session.query(func.count(Attendance.id))
                        .filter(and_(Attendance.subject == subject,
                                     Attendance.rollno == rollno))).first()[0]

    data = dict()
    data['total_present'] = total_present
    data['total_attendance'] = total_attendance

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = data
    return json.dumps(result, indent=4, default=str)


@student.route('/cumulative_attendance_summary/<string:rollno>', methods=['GET'])
def get_cumulative_attendance_summary(rollno):
    total_attendance = db.session.query(func.count(Attendance.id).label('count'), Attendance.subject) \
        .filter(Attendance.rollno == rollno) \
        .group_by(Attendance.subject).all()

    total_present = db.session.query(func.count(Attendance.id).label('count'), Attendance.subject) \
        .filter(and_(Attendance.rollno == rollno,
                     Attendance.presence_flag is True)) \
        .group_by(Attendance.subject).all()

    total_subjects = [x.subject for x in total_attendance]
    actual_subjects = [x.subject for x in total_present]
    missing_subjects = list((set(total_subjects) - set(actual_subjects)))

    [total_present.append((0l, x)) for x in missing_subjects]

    total_present.sort(key=lambda x: x[1])
    total_attendance.sort(key=lambda x: x[1])

    cumulative_attendance_summary = []

    for x, y in zip(total_present, total_attendance):
        temp = dict()
        temp["subject"] = x[1]
        temp["total_attendance"] = x[0]
        temp["total_present"] = y[0]
        cumulative_attendance_summary.append(temp)

    result = dict()

    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = cumulative_attendance_summary
    return json.dumps(result, indent=4, default=str)
