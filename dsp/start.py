# -*- coding: utf-8 -*-
import os
import logging
import yaml

from dsp.store.template_interpreter import TemplateInterpreter
from dsp.inventory.provisioning_coordinator import ProvisionCoordinator


class DsP:
    def __init__(self):
        self._logger = None
        self._playground = None
        self._interpreter = None
        self._coordinator = None

        self.initialize()

    def initialize(self):
        self._initialize_logger()
        self._interpreter = TemplateInterpreter()
        self._coordinator = ProvisionCoordinator()

    def _initialize_logger(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self.logger.addHandler(sh)

    def start(self):
        self._load_setting()
        self._playground = self._interpreter.get_playground()
        self._coordinator.provisioning(self._playground)

    def _load_setting(self):
        file_path = os.path.join(os.getcwd(), "setting.yaml")
        self._dsp_setting = self._read_yaml_file(file_path)

    def _read_yaml_file(self, _file):
        # Parse the data from YAML template.
        with open(_file, 'r') as stream:
            try:
                file_str = stream.read()
                self._logger.info("Parse YAML from the file: \n" + file_str)
                return yaml.load(file_str)
            except yaml.YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    self._logger.error(("YAML Format Error: " + _file
                                        + " (Position: line %s, column %s)" %
                                        (mark.line + 1, mark.column + 1)))
                    return None


if __name__ == '__main__':
    dsp_inst = DsP()
    dsp_inst.start()
