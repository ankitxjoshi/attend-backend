from flask import Blueprint

__author__ = 'Shivam Sharma'

teacher = Blueprint('teacher', __name__)

from . import views
