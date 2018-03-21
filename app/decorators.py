from flask_httpauth import HTTPBasicAuth
from flask import g
from models import Admin, Student

__author__ = 'Ankit Joshi'

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    admin = Admin.verify_auth_token(username_or_token)
    if not admin:
        # try to authenticate with username/password
        admin = Admin.query.filter_by(username=username_or_token).first()
        if not admin or not admin.verify_password(password):
            # first try to authenticate by token
            student = Student.verify_auth_token(username_or_token)
            if not student:
                # try to authenticate with username/password
                student = Student.query.filter_by(
                    rollno=username_or_token).first()
                if not student or not student.verify_password(password):
                    return False
            g.student = student
            return True
    g.admin = admin
    return True
