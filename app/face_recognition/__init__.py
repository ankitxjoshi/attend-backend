from flask import Blueprint

__author__ = 'Ankit Joshi'

face_recognition = Blueprint('face_recognition', __name__)

from . import views
