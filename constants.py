import os

__author__ = 'Ankit Joshi'

# OPENFACE CONSTANTS
project_path = os.path.abspath(os.path.dirname(__file__))
openface = {
    'CLASSIFIER_MODEL': project_path + '/data/feature/classifier.pkl',
    'FEATURE_DIR': project_path + '/data/feature',
    'RAW_DIR': project_path + '/data/raw',
    'ALIGNED_DIR': project_path + '/data/align',
    'TEMP_DIR': project_path + '/data/temp',
    'MAIN_LUA_SCRIPT': 'openface/batch-represent/main.lua',
    'CLASSIFIER': 'LinearSvm'
}

# FLASK CONSTANTS
flask = {
    'INSTANCE_DIR': project_path + '/instance'
}

# STRING_CONSTANTS
string = {
    'SUCCESS': 'SUCCESS',
    'USER_EXISTS': 'This user already exists',
    'MISSING_ARGS': 'All arguments have not been filled',
    'USER_DOESNT_EXISTS': 'User with the given id doesn\'t exists',
    'SERVER_ERROR': 'There was some server error',
    'BAD_IMAGE_QUALITY': 'Image is not of appropriate quality',
    'BAD_INPUT': 'Input is invalid',
    'NO_CLASS': 'No classes for today'
}

# HTTP_STATUS_CODES
status = {
    'OK': 200,
    'BAD_REQUEST': 400,
    'INTERNAL_SERVER_ERROR': 500
}
