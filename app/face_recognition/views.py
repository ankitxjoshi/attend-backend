import subprocess
from flask import jsonify

from . import face_recognition
import openface.demos.classifier_api as classifier
import openface.util.align_dlib_api as align
import constants as const
from ..decorators import auth

__author__ = 'Ankit Joshi'


# TODO: Remove the hardcoded path
@face_recognition.route('/classify')
#@auth.login_required
def classify():
    classifier_parser = classifier.Parser(['/home/ankit/PycharmProjects/attend-backend/openface/images/examples/pankaj-1.jpg'],
                                          const.openface['CLASSIFIER_MODEL'],
                                          const.openface['FEATURE_DIR'],
                                          const.openface['CLASSIFIER'])

    # Analyze the image
    identity, confidence = classifier_parser.infer()

    return jsonify(
        identity=identity,
        confidence=confidence,
        status=const.status['OK'],
        message=const.string['SUCCESS']
    )


@face_recognition.route('/train')
#@auth.login_required
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
