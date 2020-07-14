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
        self._playground = None
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

        if _prov_mode not in ["provisioning", "release"]:
            self._logger.error("Mode {} is not supported. Terminated.".format(_prov_mode))
            exit(1)

        self._playground = self.interpreter.get_playground()

        prov_result = None
        if _prov_mode == "provisioning":
            prov_result = self.coordinator.compose(self._playground)

        # elif _prov_mode == "release":
        #     prov_result = self.coordinator.release(self._playground)

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


def do_epoch(mode: str) -> float:
    tstart = datetime.datetime.now()

    dsp_inst = DsPTower()
    dsp_inst.start(mode)

    tend = datetime.datetime.now()
    elasped_time = tend - tstart

    return elasped_time.total_seconds()


if __name__ == '__main__':
    epoch = 1
    sleep_time = 0

    prov_time = do_epoch("provisioning")

    # prov_times = list()
    # release_times = list()
    #
    # for i in range(0, epoch):
    #     prov_time = do_epoch("provisioning")
    #     logging.info("Total Elasped Time for {}: {}".format(prov_time, "provisioning"))
    #     prov_times.append(prov_time)
    #     time.sleep(sleep_time)
    #
    #     release_time = do_epoch("release")
    #     logging.info("Total Elasped Time for {}: {}".format(prov_time, "provisioning"))
    #     release_times.append(release_time)
    #     time.sleep(sleep_time)
    #
    # logging.info("Elasped Time for Provisioning")
    # logging.info(prov_times)
    #
    # logging.info("Elasped Time for Release")
    # logging.info(release_times)