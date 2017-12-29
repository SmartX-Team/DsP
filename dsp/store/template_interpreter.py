# -*- coding: utf-8 -*-

import yaml

from dsp.store import repo
import logging
import httplib2




class TemplateInterpreter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._repo_manager = repo.StoreManager()

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
        except yaml.YAMLError as exc:
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
