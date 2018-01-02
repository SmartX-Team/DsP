# -*- coding: utf-8 -*-
import threading
import logging
import yaml
from dsp.inventory.inventory_manager import InventoryManager
from dsp.inventory import inventory_exceptions


class ProvisionCoordinator(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProvisionCoordinator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._logger = None
        self._setting = None
        self._playground = None
        self._installer_instances = list()

        self._inventory = InventoryManager
        self._threads_for_box_installation = list()

    def initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._inventory = InventoryManager()

    def _load_setting(self):
        self._setting = self._read_yaml_file("setting.yaml")

    def provisioning(self, playground):
        # I can't convince the needs of reordering the given template by software.
        # So, at first, I dirctly use the given template.
        # self._reorder_by_software(playground)
        self._playground = playground

        for box_with_softwares in self._playground:
            t = threading.Thread(target=self._install_softwares_to_box(), args=box_with_softwares)
            self._threads_for_box_installation.append(t)
            t.start()

        for t in self._threads_for_box_installation:
                t.join()

    def _install_softwares_to_box(self, box_with_softwares):
        software_list = box_with_softwares.software

        for software in software_list:
            installer_name = software.installer
            installer_instance = self._get_installer_by(installer_name)
            self._trigger_installation(installer_instance, box_with_softwares, software)

    def _get_installer_by(self, installer_name):
        for installer_instance in self._installer_instances:
            if installer_instance.name == installer_name:
                return installer_instance

        try:
            installer_instance = self._inventory.get_installer(installer_name)
            self._installer_instances.append(installer_instance)
        except inventory_exceptions.InventoryException as exc:
            self._logger.debug(exc.message)
            raise inventory_exceptions.ProvisioningCoordinatorException(exc.message)
        return installer_instance

    def _trigger_installation(self, installer_instance, box_with_softwares, software):
        installer_instance.install(box_with_softwares, software)

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
                    raise inventory_exceptions.ProvisioningCoordinatorException(
                        "Error occurs while loading setting.yaml")
