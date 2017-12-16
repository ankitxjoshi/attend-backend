import subprocess
import uuid
import os

from flask import jsonify, request

import constants as const
import openface.demos.classifier_api as classifier
import openface.util.align_dlib_api as align
from . import face_recognition

__author__ = 'Ankit Joshi'


@face_recognition.route('/classify', methods=['GET', 'POST'])
# @auth.login_required
def classify():
    image = request.files.get('image', '')
    file_path = const.openface['TEMP_DIR'] + '/' + str(uuid.uuid4())
    image.save(file_path)

    # file_path = '/home/ankit/PycharmProjects/attend-backend/data/temp/top'
    classifier_parser = classifier.Parser([file_path],
                                          const.openface['CLASSIFIER_MODEL'],
                                          const.openface['FEATURE_DIR'],
                                          const.openface['CLASSIFIER'])

    try:
        # Analyze the image
        identity, confidence = classifier_parser.infer()
    except:
        return jsonify(
            data=None,
            status=const.status['INTERNAL_SERVER_ERROR'],
            message=const.string['BAD_IMAGE_QUALITY']
        )

    print identity
    data = dict()
    data['identity'] = identity
    data['confidence'] = str(confidence)

    return jsonify(
        data=data,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@face_recognition.route('/train')
# @auth.login_required
def train():
    classifier_parser = classifier.Parser(None,
                                          const.openface['CLASSIFIER_MODEL'],
                                          const.openface['FEATURE_DIR'],
                                          const.openface['CLASSIFIER'])

    align_parser = align.Parser(const.openface['RAW_DIR'], const.openface['ALIGNED_DIR'])

    # Preprocess the raw images
    align_parser.alignMain()

    # Generate Representations
    subprocess.call([const.openface['MAIN_LUA_SCRIPT']])

    # Create the Classification Model
    classifier_parser.train()

    return jsonify(
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )
