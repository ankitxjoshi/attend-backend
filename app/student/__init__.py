from flask import Blueprint

__author__ = 'Shivam Sharma'

student = Blueprint('student', __name__)

from . import views
