import datetime
import json

from flask import jsonify, g
from sqlalchemy import *

import constants as const
from . import student
from .. import db
from ..decorators import auth
from ..models import Student, TimeTable
from ..models import Period, Classroom
from ..models import Staff, Attendance, TeacherAttendance
import itertools

__author__ = 'Shivam Sharma'


# write the routes below
@student.route('/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.student.generate_auth_token(600)

    data = dict()
    data['token'] = token
    data['duration'] = 600

    return jsonify(
        status=const.status['OK'],
        data=data,
        message=const.string['SUCCESS'],
    )


@student.route('/classesOfDay/<string:rollno>', methods=['GET'])
def get_classes_of_day(rollno):
    # get the section and year
    student_details = Student.query.filter_by(rollno=rollno).first()
    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    section, year = student_details.section, student_details.year

    now = datetime.datetime.now()
    day = now.strftime('%A')

    time_table_details = (db.session.query(
        TimeTable.subject.label('subject'),
        TimeTable.location.label('classroom'),
        TimeTable.period_id.label('period'),
        Staff.name.label('faculty_name'),
        Period.start_time.label('begin_time'),
        Period.end_time.label('end_time'),
        Classroom.bluetooth_address.label('bluetooth_address'))
                          .join(Period)
                          .join(Staff)
                          .join(Classroom)
                          .filter(and_(TimeTable.day == day,
                                       TimeTable.section == section,
                                       TimeTable.year == year))
                          ).all()

    timetable_list = ['subject', 'classroom', 'faculty_name', 'begin_time',
                      'end_time', 'period', 'bluetooth_address']
    timetable = [dict((name, getattr(x, name)) for name in timetable_list)
                 for x in
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

    data_list = ['branch', 'email', 'name',
                 'phoneno', 'rollno', 'section',
                 'year']
    data = dict((name, getattr(student, name)) for name in data_list)
    print 'data--------------', data
    return jsonify(
        data=data,
        image_path=student.image_url,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@student.route('/attendance_details_for_subject/' +
               '<string:rollno>/<string:subject>',
               methods=['GET'])
def get_attendance_details_for_subject(rollno, subject):
    student = Student.query.filter_by(rollno=rollno).first()

    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )
    section = getattr(student, 'section')
    year = getattr(student, 'year')

    total_present = db.session.query(Attendance.date,
                                     Attendance.period_id.label('period')) \
        .filter(and_(Attendance.rollno == rollno,
                     Attendance.subject == subject)) \
        .all()
    total_attendance = db.session.query(
                       TeacherAttendance.date,
                       TeacherAttendance.period_id.label('period')) \
        .filter(and_(TeacherAttendance.year == year,
                     and_(TeacherAttendance.subject == subject,
                          TeacherAttendance.section == section))) \
        .all()

    present_details = [dict((name, getattr(x, name))
                            for name in ['date', 'period'])
                       for x in total_present]
    attendance_details = [dict((name, getattr(x, name))
                               for name in ['date', 'period'])
                          for x in total_attendance]
    absent_details = list(itertools.ifilterfalse(
        lambda x: x in present_details, attendance_details))
    present_details = list(itertools.ifilter(
        lambda x: x in present_details, attendance_details))

    data_list = list()
    for x in present_details:
        x['presence_flag'] = True
        data_list.append(x)
    for x in absent_details:
        x['presence_flag'] = False
        data_list.append(x)
    data_list = sorted(data_list, key=lambda k: (k['date'], k['period']))

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = data_list
    return json.dumps(result, indent=4, default=str)


@student.route('/attendance_summary_for_subject/' +
               '<string:rollno>/<string:subject>',
               methods=['GET'])
def get_attendance_summary_for_subject(rollno, subject):
    student = Student.query.filter_by(rollno=rollno).first()

    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )

    section = getattr(student, 'section')
    year = getattr(student, 'year')
    total_present = db.session.query(Attendance.date,
                                     Attendance.period_id.label('period')) \
        .filter(Attendance.rollno == rollno, Attendance.subject == subject) \
        .all()
    total_attendance = db.session.query(
                       TeacherAttendance.date,
                       TeacherAttendance.period_id.label('period')) \
        .filter(TeacherAttendance.year == year,
                TeacherAttendance.subject == subject,
                TeacherAttendance.section == section) \
        .all()

    present_details = [dict((name, getattr(x, name))
                            for name in ['date', 'period'])
                       for x in total_present]
    attendance_details = [dict((name, getattr(x, name))
                               for name in ['date', 'period'])
                          for x in total_attendance]
    present_details = list(itertools.ifilter(
        lambda x: x in present_details, attendance_details))

    total_present = len(present_details)
    total_attendance = len(attendance_details)

    data = dict()
    data['total_present'] = total_present
    data['total_attendance'] = total_attendance

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = data
    return json.dumps(result, indent=4, default=str)


@student.route('/cummulative_attendance_summary/' +
               '<string:rollno>',
               methods=['GET'])
def get_cummulative_attendance_summary(rollno):
    student = Student.query.filter_by(rollno=rollno).first()
    if not student:
        return jsonify(
            status=const.status['BAD_REQUEST'],
            message=const.string['USER_DOESNT_EXISTS']
        )
    section = getattr(student, 'section')
    year = getattr(student, 'year')
    total_attendance = db.session.query(
                       TeacherAttendance.subject,
                       func.count(TeacherAttendance.id)
                       .label('total_attendance')) \
        .filter(TeacherAttendance.section == section,
                TeacherAttendance.year == year) \
        .group_by(TeacherAttendance.subject) \
        .all()

    total_present = db.session.query(
                    Attendance.subject,
                    func.count(Attendance.id).label('total_present')) \
        .filter(Attendance.rollno == rollno) \
        .group_by(Attendance.subject) \
        .all()

    total_subjects = [x[0] for x in total_attendance]
    actual_subjects = [x[0] for x in total_present]
    missing_subjects = list((set(total_subjects) - set(actual_subjects)))

    [total_present.append((x, 0l)) for x in missing_subjects]

    total_present.sort(key=lambda x: x[0])
    total_attendance.sort(key=lambda x: x[0])

    cummulative_attendance_summary = list()

    for x, y in zip(total_present, total_attendance):
        temp = dict()
        temp['subject'] = x[0]
        temp['total_attendance'] = y[1]
        temp['total_present'] = x[1]
        print temp
        cummulative_attendance_summary.append(temp)
    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = cummulative_attendance_summary
    return json.dumps(result, indent=4, default=str)


@student.route('/mark_attendance/<string:rollno>/' +
               '<string:subject>/<string:period_id>',
               methods=['GET'])
def mark_attendance(rollno, subject, period_id):
    period = Period.query.filter_by(id=period_id).first()
    now = datetime.datetime.now()

    start_time = datetime.datetime.strptime(str(period.start_time), '%H:%M:%S')
    start_time = now.replace(hour=start_time.time().hour,
                             minute=start_time.time().minute,
                             second=start_time.time().second,
                             microsecond=0)

    end_time = datetime.datetime.strptime(str(period.end_time), '%H:%M:%S')
    end_time = now.replace(hour=end_time.time().hour,
                           minute=end_time.time().minute,
                           second=end_time.time().second,
                           microsecond=0)

    if start_time <= now <= end_time:
        attendance = Attendance(period_id=period_id,
                                rollno=rollno,
                                subject=subject
                                )

        db.session.add(attendance)
        db.session.commit()
        data = dict()
        data['marked'] = 'true'

    else:
        data = dict()
        data['marked'] = 'false'

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = data
    return json.dumps(result, indent=4, default=str)
