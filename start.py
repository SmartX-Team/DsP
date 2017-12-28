# -*- coding: utf-8 -*-
import os
import logging
import yaml

from tmpl_interp import TemplateInterpreter
from prov.prov import ProvisionCoordinator


class DsPInstaller:
    def __init__(self):
        self._logger = None

        self._boxes_info = None
        self._dsp_setting = None
        self._template = None

        self._tmpl_interp = None
        self._prov_coordi = None

    def initialize(self):
        self._initialize_logger()
        self._tmpl_interp = TemplateInterpreter()
        self._prov_coordi = ProvisionCoordinator()

    def _initialize_logger(self):
        self.logger = logging.getLogger("ovn")
        self.logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self.logger.addHandler(sh)

    def start(self):
        self._load_configurations()
        # Get required installation tools from inventory
        # Trigger provisioning coordinator with those tools and parsed template
        prov_info = self._tmpl_interp.interp_tmpl(tmpl_path)
        self._prov_coordi.prov_playground(prov_info)

    def _load_configurations(self):
        try:
            self._load_dsp_setting()
            self._load_box_info()
            self._load_playground_template()
        except FileExistsError as exc:
            print(exc.args)
        except yaml.YAMLError as exc:
            print(exc.args)

    def _load_dsp_setting(self):
        file_path = os.path.join(os.getcwd(), "setting.yaml")
        self._dsp_setting = self._get_yaml_obj_from(file_path)

    def _load_box_info(self):
        file_path = os.path.join(os.getcwd(), "repo", "box.yaml")
        self._boxes_info = self._get_yaml_obj_from(file_path)

    def _load_playground_template(self):
        self._read_playground_template_file()
        self._parse_playground_template()
        self._validate_playground_template()

    def _read_playground_template_file(self):
        file_path = os.path.join(os.getcwd(), "repo", "playground.yaml")
        self._template = self._get_yaml_obj_from(file_path)

    def _parse_playground_template(self):
        pass

    def _validate_playground_template(self):
        # Will be implemented
        pass

    def _get_yaml_obj_from(self, yaml_file):
        with open(yaml_file, 'r') as stream:
            return yaml.load(stream)



if __name__ == '__main__':
    dsp_inst = DsPInstaller()
    dsp_inst.start()
