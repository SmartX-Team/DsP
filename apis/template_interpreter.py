import os
from flask import Flask, request
from .. import template_interpreter

"""
Template Interpreter should have interfaces to Secured Repository Manager
instance. Since Secured Repository Manager doesn't have any REST API,
the Interpreter should be contact points to outside.

Input: Box Setting File, PG Template File
Output: Supervisor Parameters for the specific box

Required REST APIs for Template Interpreter.
    - GET Boxes list (/template/box)
    - GET Box Details (/template/box/<string:hostname>
    - GET Playground Template (/template/playground)
    - POST set Playground Template (/template/playground/)
      (template file path)
    - POST interpret Playground Template (/template/playground/interpret)
      (box template yaml, playground template yaml)
"""


app = Flask(__name__)


@app.route("/template/", methods=['GET'])
def get_template_interpreter():
    return "Template Interpreter is alive :)"


@app.route("/dsp/template/box/", methods=['POST'])
def get_box_settings():
    _cfg_path = request.data
    if os.path.exists(_cfg_path):
        _l = interpreter.get_box_settings(_cfg_path)
        return yaml.dump(_l)
    else:
        return "The given path for Box Setting is not valid: "+_cfg_path


@app.route("/dsp/template/playground/", methods=['POST'])
def get_dsp_template():
    _template_path = request.data
    if os.path.exists(_template_path):
        _l = interpreter.get_dsp_template(_template_path)
        return yaml.dump(_l)
    else:
        return "The given path for Playground Template is not valid: " \
               + _template_path


@app.route("/dsp/template/interpret", methods=['POST'])
def interpret_dsp_template():
    interpreter.logger.info("Receive a request: interpret_dsp_template()")
    interpreter.logger.info(request.data)

    try:
        y = yaml.load(request.data)
    except yaml.YAMLError as exc:
        if hasattr(exc, 'problem_mark'):
            mark = exc.problem_mark
            interpreter.logger.error("Error Position: (%s:%s)" %
                              (mark.line + 1, mark.column + 1))
            return None

    if not interpreter.valid_box_setting(y[0]):
        return "Yaml format for Box setting is not valid"
    elif not interpreter.valid_dsp_template(y[1]):
        return "DsP Template is not valid"

    interpreter.interpret_dsp_template(y[0], y[1])
    return "404"


@app.route("/dsp/template/interpret/box/<string:hostname>", methods=['POST'])
def interpret_dsp_template_for_box():
    return "400"