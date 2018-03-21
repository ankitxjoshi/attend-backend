from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate


from config import app_config

db = SQLAlchemy()
auth = HTTPBasicAuth()

__author__ = 'Ankit Joshi'


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    db.init_app(app)

    @app.route('/api/health', methods=['GET'])
    def health():
        return 'SUCCESS', 200

    migrate = Migrate(app, db)

    from app import models

    from face_recognition import face_recognition as face_recognition_blueprint
    app.register_blueprint(face_recognition_blueprint,
                           url_prefix='/api/openface')

    from admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin')

    # Route for student
    from student import student as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/api/student')

    # Route for teacher
    from teacher import teacher as teacher_blueprint
    app.register_blueprint(teacher_blueprint, url_prefix='/api/teacher')

    return app
