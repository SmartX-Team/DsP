# -*- coding: utf-8 -*-
import threading
import logging
import yaml
from multiprocessing import Process, Queue, Lock
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
        self.initialize()

    def initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self._inventory = InventoryManager()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def _load_setting(self):
        self._setting = self._read_yaml_file("setting.yaml")

    def provisioning(self, playground):
        # I can't convince the needs of reordering the given template by software.
        # So, at first, I directly use the given template.
        # self._reorder_by_software(playground)
        self._playground = playground
        scheduled_list = self.scheduling(playground)
        self._logger.debug(scheduled_list)

        procs = list()
        result_queue = Queue()

        for box_with_softwares in self._playground:
            proc = Process(target=self._install_softwares_to_box, args=(box_with_softwares, result_queue,))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

        return result_queue

    def scheduling(self, playground):
        scheduled = list()

        # sched_key = "type"
        sched_order = ("physical.box", "virtual.box")

        for e in sched_order:
            e_dict = dict()
            e_dict[e] = list()
            scheduled.append(e_dict)

        for box in playground:
            for e in scheduled:
                if box.type in e.keys():
                    e[box.type].append(box)

        return scheduled

    def _install_softwares_to_box(self, box_with_softwares, result_queue):
        self._logger.debug("A New Installing Process Started. Box: {}".format(box_with_softwares.name))
        software_list = box_with_softwares.software
        box_prov_res = list()

        for software in software_list:
            installer_name = software.installer
            installer_instance = self._get_installer(installer_name)
            self._logger.debug("Starting Installation. Box: {}, Software: {}, Installer: {}".format(
                box_with_softwares.name,
                software.name,
                installer_instance.name)
            )
            sw_res = self._trigger_installation(installer_instance,
                                                box_with_softwares,
                                                software)
            box_prov_res.append(sw_res)

        self._logger.debug("A Process Finished. Box: {}".format(box_with_softwares.name))
        result_queue.put([box_with_softwares.name, box_prov_res])

    def _trigger_installation(self, installer_instance, box_with_softwares, target_software):
        install_result = installer_instance.install(box_with_softwares, target_software)
        return install_result

    def release(self, playground):
        self._playground = playground

        procs = list()
        result_queue = Queue()

        for box_with_softwares in self._playground:
            proc = Process(target=self._uninstall_softwares_from_box, args=(box_with_softwares, result_queue,))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

        return result_queue

    def _uninstall_softwares_from_box(self, box_with_softwares, result_queue):
        self._logger.debug("A New Uninstalling Process Started. Box: {}".format(box_with_softwares.name))
        software_list = box_with_softwares.software
        box_rel_res = list()

        for software in software_list:
            installer_name = software.installer
            installer_instance = self._get_installer(installer_name)
            self._logger.debug("Starting Un-installation. Box: {}, Software: {}, Installer: {}".format(
                box_with_softwares.name,
                software.name,
                installer_instance.name)
            )
            rel_res = self._trigger_uninstallation(installer_instance,
                                                                        box_with_softwares,
                                                                        software)
            box_rel_res.append(rel_res)

        self._logger.debug("A Process Finished. Box: {}".format(box_with_softwares.name))
        result_queue.put([box_with_softwares.name, box_rel_res])

    def _trigger_uninstallation(self, installer_instance, box_with_softwares, target_software):
        install_result = installer_instance.uninstall(box_with_softwares, target_software)
        return install_result

    def _get_installer(self, installer_name):

        for installer_instance in self._installer_instances:
            if installer_instance.name == installer_name:
                return installer_instance

        try:
            installer_instance = self._inventory.get_installer(installer_name)
            self._installer_instances.append(installer_instance)

        except inventory_exceptions.InventoryException as exc:
            self._logger.debug(exc)
            raise inventory_exceptions.ProvisioningCoordinatorException(exc)

        return installer_instance

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
