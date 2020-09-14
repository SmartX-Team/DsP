# -*- coding: utf-8 -*-
import os
import logging
import yaml
import datetime

from tower.template_interpreter import TemplateInterpreter
from tower.provisioning_coordinator import ProvisionCoordinator


class DsPTower:
    def __init__(self):
        self._logger: logging
        self._physical_topology = None
        self._desired_playground = None
        self.interpreter: TemplateInterpreter = TemplateInterpreter()
        self.coordinator: ProvisionCoordinator = ProvisionCoordinator()

        self._initialize_logger()
        self._load_setting()

    def _initialize_logger(self):
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self._logger.addHandler(sh)

    def _load_setting(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "setting.yaml")
        self._dsp_setting = self._read_yaml_file(file_path)

    def start(self, _prov_mode: str):

        # self._physical_topology = self.interpreter.get_physical_topology()
        self._physical_topology, self._desired_playground = self.interpreter.get_playground()

        prov_result = None
        if _prov_mode == "compose":
            prov_result = self.coordinator.compose(self._physical_topology, self._desired_playground)

        elif _prov_mode == "update":
            prov_result = self.coordinator.update(self._physical_topology, self._desired_playground)

        elif _prov_mode == "release":
            prov_result = self.coordinator.release(self._physical_topology, self._desired_playground)

        else:
            self._logger.error("Mode {} is not supported. Terminated.".format(_prov_mode))
            exit(1)

        if prov_result:
            while not prov_result.empty():
                self._logger.debug(prov_result.get())

    def _read_yaml_file(self, _file: str) -> dict or None:
        # Parse the data from YAML template.
        with open(_file, 'r') as stream:
            try:
                file_str = stream.read()
                self._logger.debug("Parse YAML from the file: \n" + file_str)
                if file_str:
                    return yaml.load(file_str, Loader=yaml.FullLoader)
                else:
                    return None
            except yaml.YAMLError as exc:
                if hasattr(exc, 'problem_mark'):
                    mark = exc.problem_mark
                    self._logger.error(("YAML Format Error: " + _file
                                        + " (Position: line %s, column %s)" %
                                        (mark.line + 1, mark.column + 1)))
                    return None
