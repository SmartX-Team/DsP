# -*- coding: utf-8 -*-
import os
import logging
import yaml
from multiprocessing import Process, Queue
from post.inventory.inventory_manager import InventoryManager
from post.inventory import inventory_exceptions

from abstracted_component.cluster import Cluster
from abstracted_component.box import Box
from abstracted_component.function import Function
from typing import List, Dict

# Todo: Remove setting.yaml files of installer tools
# Todo: When creating installer tools, inject their configuration


class DsPPost(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DsPPost, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._logger: logging
        self._playground: dict or None = None
        self._boxes: List[Box] = list()
        self._functions: List[Function] = list()

        self._setting = self._load_setting()
        self._inventory: InventoryManager = InventoryManager()
        self._initialize_logger()

    def _initialize_logger(self):
        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self._logger.addHandler(sh)

    def _load_setting(self):
        file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "setting.yaml")
        return self._read_yaml_file(file_path)
    #
    # Public Methods that are called by API servers.
    #
    def reload_cluster(self, cluster_topology: dict):
        for box_desc in cluster_topology["cluster"]["boxes"]:
            box_desc["where"] = cluster_topology["cluster"]["name"]
            matched = False
            for prev_box in self._boxes:
                if prev_box.name == box_desc["name"] and prev_box.where == box_desc["where"]:
                    # Update the subset of the attributes
                    prev_box.account = box_desc["account"]
                    prev_box.network = box_desc["network"]
                    matched = True
                    break

            if not matched:
                box_instance = Box.create_from_dict(box_desc)
                self._boxes.append(box_instance)

    def compose(self, playground: Cluster):
        self._logger.debug("Compose started")
        self._playground = playground
        # self._reorder_by_software(playground)
        # scheduled_list = self.scheduling(playground)
        # self._logger.debug("Provisioning order: {}".format(scheduled_list))

        result_queue = Queue()

        if playground.boxes:
            self._logger.debug("1")
            _proc_method = self._provision_box
            # self._in_parallel(_proc_method, playground.boxes, result_queue)

        if playground.functions:
            self._logger.debug("2")
            _proc_method = self._provision_func
            self._in_parallel(_proc_method, playground.functions, result_queue)

        return result_queue

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

    def update_function(self, funcs: List[Function]):
        # In this version, this method can only support functions.

        for func in funcs:
            # extract a physical box hosting the function
            # extract the function name
            # call APIs of the box with new rules
            # return the update result
            pass
        pass

    def get_installers(self):
        return self._inventory.get_installers()

    def get_installer(self, installer_name: str):
        return self._inventory.get_installer(installer_name)

    #
    # Private Methods
    #
    def _in_parallel(self, _method, compose_elements: List[Box] or List[Function], result_queue: Queue):
        self._logger.debug("3")
        procs = list()

        for elem in compose_elements:
            proc = Process(target=_method,
                           args=(elem, self._inventory, result_queue,))

            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

    def _scheduling(self, playground):
        # I can't convince the needs of reordering the given template by software.
        # So, I simply follow the order written in the given template.

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

    def _get_loaded_box(self, box_name):
        for b in self._boxes:
            if b.name == box_name:
                return b

        return None

    def _provision_box(self, desire_box_desc: Box, _inven_mgr: InventoryManager, result_queue: Queue):
        self._logger.info("A New Installing Process Started. Name: {}".format(desire_box_desc.name))

        target_box = self._get_loaded_box(desire_box_desc.name)
        if not target_box:
            self._logger.error("The target box \"{}\" is not managed by the post".format(desire_box_desc.name))
            return None

        software_list = desire_box_desc.software

        provision_log = list()

        for software in software_list:
            installer_name = software.installer
            installer_instance = _inven_mgr.get_installer(installer_name)

            self._logger.info("Starting Installation. Box: {}, Software: {}, Installer: {}".format(
                desire_box_desc.name,
                software.name,
                installer_instance.name)
            )

            # res = self._execute_installer(installer_instance, target_box, software)
            # self._logger.debug(res)
            # provision_log.append(res)

        self._logger.info("A Process Finished. Box: {}".format(desire_box_desc.name))
        result_queue.put([desire_box_desc.name, provision_log])

    def _provision_func(self, func_desc: Function, _inven_mgr: InventoryManager, result_queue: Queue):
        self._logger.debug("A new provisioning process started. Function: {}".format(func_desc.name))

        provision_log = list()

        installer_name = func_desc.installer
        installer_instance = _inven_mgr.get_installer(installer_name)

        self._logger.debug("Starting Installation. Function: {}, Installer: {}".format(
            func_desc.name,
            installer_instance.name)
        )

        box_name = func_desc.where.split(".")[1]
        # box_desc = self._find_box_desc(box_name)
        target_box = self._get_loaded_box(box_name)

        res = "A box for the function: {}".format(target_box.name)
        res = self._execute_installer(installer_instance, target_box, func_desc)
        provision_log.append(res)
        self._logger.debug(res)

        self._logger.debug("A Process Finished. Function: {}".format(target_box.name))
        result_queue.put([target_box.name, provision_log])

    # def _find_box_desc(self, box_name: str):
    #     for box_desc in self._boxes_desc:
    #         if box_desc.name == box_name:
    #             return box_desc
    #     return None

    def _execute_installer(self, installer_instance, box_with_softwares, target_software):
        install_result = installer_instance.install(box_with_softwares, target_software)
        return install_result

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
            # rel_res = self._trigger_uninstallation(installer_instance,
            #                                                             box_with_softwares,
            #                                                             software)
            rel_res = "hello"
            box_rel_res.append(rel_res)

        self._logger.debug("A Process Finished. Box: {}".format(box_with_softwares.name))
        result_queue.put([box_with_softwares.name, box_rel_res])

    def _trigger_uninstallation(self, installer_instance, box_with_softwares, target_software):
        install_result = installer_instance.uninstall(box_with_softwares, target_software)
        return install_result

    def _get_installer(self, installer_name):
        try:
            installer_instance = self._inventory.get_installer(installer_name)
            return installer_instance

        except inventory_exceptions.InventoryException as exc:
            self._logger.debug(exc)
            raise inventory_exceptions.ProvisioningCoordinatorException(exc)

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


if __name__ == "__main__":
    dsp_post = DsPPost()
    print("Hello World")
