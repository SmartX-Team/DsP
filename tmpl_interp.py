# -*- coding: utf-8 -*-

import yaml
import os

from repo import repo
import logging
from flask import Flask, request
import httplib2

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
    except yaml.YAMLError, exc:
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


class TemplateInterpreter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._repo_manager = repo.SecuredRepoMgr()

        self.logger = logging.getLogger("TemplateInterpreter")
        self.logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fm)
        self.logger.addHandler(ch)

    def get_box_hostnames(self, __box_config_file):
        self.logger.debug("Enter get_box function")
        l = self._repo_manager.read_file(__box_config_file)

        try:
            _box_cfg = yaml.load(l)
        except yaml.YAMLError, exc:
            if hasattr(exc, 'problem_mark'):
                mark = exc.problem_mark
                self.logger.error("Error Position: (%s:%s)" %
                                  (mark.line+1, mark.column+1))
                return None

        _box_name_list = list()
        for box in _box_cfg:
            if 'hostname' in box:
                _box_name_list.append(box['hostname'])

        self.logger.debug(_box_name_list)
        return _box_name_list

    def get_box_settings(self, __box_config_file):
        self.logger.debug("Enter get_box_settings function")
        return self._repo_manager.read_file(__box_config_file)

    def get_dsp_template(self, __template_file):
        self.logger.debug("Enter get_dsp_template function")
        return self._repo_manager.read_file(__template_file)

    def valid_box_setting(self, __box_setting):
        return True

    def valid_dsp_template(self, __dsp_template):
        return True

    def interpret_dsp_template(self, __box_setting, __dsp_template):
        """
        make installer list
        For each installer
            make parameter list

            for each box
                extract required parameters from installer's setting.xml
                extract parameter from box
                fill empty value
                add the filled parameter into the list
            add parameter list

        Get Supervisors list
        Get Software Priority List
        Map supervisors which can install each software to software key
        """
        http = httplib2.Http()
        resp, content = http.request(
            "http://localhost:22730/inventory/supervisor/")
        _supervisor_list = yaml.load(content)

        resp, content = http.request(
            "http://localhost:22730/inventory/supervisor/priority")
        _sw_prio = yaml.load(content)

        map_sv_for_prio_sw = dict()
        for prio_sw in _sw_prio['priority']:
            sv_for_sw = list()
            for sv in _supervisor_list:
                if prio_sw in sv['target_software']:
                    sv_for_sw.append(sv)
            map_sv_for_prio_sw[prio_sw] = sv_for_sw
        self.logger.debug(map_sv_for_prio_sw)

        map_sv_for_indep_sw = dict()
        for indep_sw in _sw_prio['independent']:
            sv_for_sw = list()
            for sv in _supervisor_list:
                if indep_sw in sv['target_software']:
                    sv_for_sw.append(sv)
            map_sv_for_indep_sw[indep_sw] = sv_for_sw
        self.logger.debug(map_sv_for_indep_sw)

interpreter = TemplateInterpreter()
app.run(port="22732")
