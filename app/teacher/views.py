from flask import abort, request, jsonify, g, url_for
import os
import json
import datetime
from . import teacher
from .. import db
from ..models import Admin, Student, TimeTable
from ..models import Period, Classroom, Staff
from ..models import Attendance, TeacherAttendance
from ..decorators import auth
import constants as const
import itertools
from sqlalchemy import *

__author__ = 'Shivam Sharma'

# write the routes below


@teacher.route('/classesOfDay/<string:staff_id>/<string:day>', methods=['GET'])
def get_classes_of_day(staff_id, day):
    time_table_details = (db.session.query(
                            TimeTable.subject.label('subject'),
                            TimeTable.section.label('section'),
                            TimeTable.year.label('year'),
                            TimeTable.location.label('classroom'),
                            TimeTable.period_id.label('period'),
                            Period.start_time.label('begin_time'),
                            Period.end_time.label('end_time'))
                          .join(Period)
                          .filter(and_(TimeTable.day == day,
                                       TimeTable.staff_id == staff_id))
                          ).all()

    timetable_list = ['subject', 'classroom', 'section',
                      'year', 'period', 'begin_time',
                      'end_time']
    timetable = [dict((name, getattr(x, name))
                      for name in timetable_list) for x in time_table_details]

    result = dict()
    if not timetable:
        result['status'] = const.status['OK']
        result['message'] = const.string['NO_CLASS']
        return json.dumps(result, indent=4, default=str)

    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = timetable
    return json.dumps(result, indent=4, default=str)


@teacher.route('/viewAttendance/<string:section>/<string:year>' +
               '/<string:subject>/<string:staff_id>',
               methods=['GET'])
def get_attendace(section, subject, year, staff_id):
    year = int(year)
    total_attendance = db.session.query(
                       TeacherAttendance.date,
                       TeacherAttendance.period_id.label('period'))\
        .filter(TeacherAttendance.year == year,
                TeacherAttendance.subject == subject,
                TeacherAttendance.section == section,
                TeacherAttendance.staff_id == staff_id) \
        .all()
    date_period_list = [(x.date, x.period) for x in total_attendance]
    rollno_details = db.session.query(Student.rollno.label('rollno'))\
        .filter(Student.section == section)\
        .all()
    all_rollno_list = [x.rollno for x in rollno_details]

    result_data = list()

    for x in date_period_list:

        #  TODO: Refractor code
        # attendance_for_day = db.session.query(Attendance.rollno)\
        #                                .filter(
        #                          Attendance.date == x[0],
        #                          Attendance.period_id == x[1],
        #                          Attendance.subject == subject,
        #                          Attendance.rollno.in_(all_rollno_list)
        #                                 .all()

        rollno_list = [y.rollno for y in attendance_for_day]

        temp = dict()
        temp['date'] = x[0]
        temp['period'] = x[1]
        temp['details'] = list()
        for y in rollno_list:
            temp_dict = dict()
            temp_dict['rollno'] = y
            temp_dict['presence_flag'] = True
            temp['details'].append(temp_dict)
        absent_rollno_list = list(itertools.ifilterfalse(
            lambda x: x in rollno_list, all_rollno_list))
        for y in absent_rollno_list:
            temp_dict = dict()
            temp_dict['rollno'] = y
            temp_dict['presence_flag'] = False
            temp['details'].append(temp_dict)
        # sort the temp details
        temp['details'] = sorted(temp['details'], key=lambda k: k['rollno'])
        result_data = sorted(
            result_data, key=lambda k: (k['date'], k['period']))
        result_data.append(temp)

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['data'] = result_data
    return json.dumps(result, indent=4, default=str)


@teacher.route('/ editAttendance/<string: staff_id > /+
               '<string:rollno>/<string:subject>/' +
               '<string: date > / < string: period > /+' +
               '<string:mark_flag>',
               methods=['PUT'])
def edit_attendance(staff_id, rollno, subject, date, period, mark_flag):
    # date in dd-mm-yy  check for period in time table
    period = int(period)
    date = datetime.datetime.strptime(date[2:], '%y-%m-%d')
    print date
    day = date.strftime('%A')
    print date, day
    student = Student.query.filter_by(rollno=rollno).first()
    section = student.section
    year = student.year
    # TODO: Code needs refractoring
    # timetable_entry = db.session.query(TimeTable.id)\
    #                             .filter(TimeTable.period_id == period,
    #                                     TimeTable.year == year,
    #                                     TimeTable.subject == subject,
    #                                     TimeTable.section == section,
    #                                     TimeTable.day == day,
    #                                     TimeTable.staff_id == staff_id)
    #     .first()

    if timetable_entry is None:
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['BAD_INPUT']
        return json.dumps(result, indent=4, default=str)

    if mark_flag == 'Present':
        # TODO: Code needs refractoring
        # attendance_entry = db.session.query(Attendance.rollno)\
        #                         .filter(Attendance.date == date,
        #                                 Attendance.period_id == period,
        #                                 Attendance.subject == subject,
        #                                 Attendance.rollno == rollno)\
        #                         .first()
        if attendance_entry is None:
            attendance = Attendance(
                rollno=rollno, date=date, period_id=period, subject=subject)
            db.session.add(attendance)
            db.session.commit()
    else:
        pass
        # TODO: Code needs refractoring
        # attendance_entry = db.session.query(Attendance.rollno)\
        #                     .filter(Attendance.date == date,
        #                             Attendance.period_id == period,
        #                             Attendance.subject == subject,
        #                             Attendance.rollno == rollno)\
        #                     .delete()
    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    return json.dumps(result, indent=4, default=str)

# TODO: Change route
# @teacher.route('/markSelfAttendance/<string:subject>/' +
#                '<string:staff_id>/<string:section>/' +
#                '<string:year>/<string:period>', ]
#                methods = ['GET'])


def mark_self_attendance(subject, staff_id, section, year, period):
    now = datetime.datetime.now()
    date = now.strftime('%y-%m-%d')
    year = int(year)
    period = int(period)
    day = now.strftime('%A')
    print day
    # check whether the period exsists or not
    # TODO: Code needs refractoring
    # timetable_entry = db.session.query(TimeTable.id)\
    #     .filter(and_(TimeTable.period_id == period,
    #                  and_(TimeTable.year == year,
    #                       and_(TimeTable.subject == subject,
    #                            and_(TimeTable.section == section,
    #      and_(TimeTable.day == day, TimeTable.staff_id == staff_id))))))\
    #    .first()
    if timetable_entry is None:
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['BAD_INPUT']
        return json.dumps(result, indent=4, default=str)
    # TODO: Code needs refractoring
    # teacher_attendance_entry = db.session.query(TeacherAttendance.id)\
    #     .filter(and_(TeacherAttendance.date == date,
    #     and_(TeacherAttendance.period_id == period,
    #         and_(TeacherAttendance.section == section,
    #         and_(TeacherAttendance.year == year,
    #     and_(TeacherAttendance.subject == subject,
    #    TeacherAttendance.staff_id == staff_id))))))\
    #     .first()
    if teacher_attendance_entry is None:
        teacher_attendance = TeacherAttendance(staff_id=staff_id,
                                               date=date,
                                               period_id=period,
                                               subject=subject,
                                               section=section,
                                               year=year)
        db.session.add(teacher_attendance)
        db.session.commit()
    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    return json.dumps(result, indent=4, default=str)


@teacher.route('/createUser', methods=['POST'])
def new_teacher():
    staff_id = request.json.get('staff_id')
    name = request.json.get('name')
    passwod = request.json.get('password')
    # missing arguments
    if name is None or passwod is None or staff_id is None:
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['MISSING_ARGS']
        return json.dumps(result, indent=4, default=str)

    if Staff.query.filter_by(id=staff_id).first() is not None:
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['MISSING_ARGS']
        return json.dumps(result, indent=4, default=str)

    teacher = Staff(id=staff_id, name=name)
    teacher.hash_password(passwod)
    db.session.add(teacher)
    db.session.commit()
    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['staff_id'] = teacher.id
    return json.dumps(result, indent=4, default=str)


@teacher.route('/login', methods=['POST'])
def login():
    staff_id = request.json.get('staff_id')
    passwod = request.json.get('password')
    # missing arguments
    if passwod is None or staff_id is None:
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['MISSING_ARGS']
        return json.dumps(result, indent=4, default=str)
    staff = Staff.query.filter_by(id=staff_id).first()
    if not staff or not staff.verify_password(passwod):
        result = dict()
        result['status'] = const.status['BAD_REQUEST']
        result['message'] = const.string['USER_DOESNT_EXISTS']
        return json.dumps(result, indent=4, default=str)

    result = dict()
    result['status'] = const.status['OK']
    result['message'] = const.string['SUCCESS']
    result['staff_id'] = staff.id
    return json.dumps(result, indent=4, default=str)
