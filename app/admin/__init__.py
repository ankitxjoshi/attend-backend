from flask import Blueprint

__author__ = 'Ankit Joshi'

admin = Blueprint('admin', __name__)

from . import views
