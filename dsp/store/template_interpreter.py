# -*- coding: utf-8 -*-

from dsp.store.store_manager import StoreManager
import logging
import store_exceptions

from dsp.abstracted_component.box import Box, NetworkInterface
from dsp.abstracted_component.software import Software


class TemplateInterpreter:
    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._store = None
        self._logger = None
        self._boxes = None
        self._template = None
        self._playground = None
        self.initialize()

    def initialize(self):
        self._store = StoreManager()
        self._logger = logging.getLogger(self.__class__.__name__)

    def get_playground(self):
        self._get_file_instances()
        self._validate_file_format()
        self._playground = self._create_playground()
        return self._playground

    def _get_file_instances(self):
        self._template = self._store.get_template()
        self._boxes = self._store.get_boxes()

    def _validate_file_format(self):
        self._validate_template_format(self._template)
        self._validate_boxes_format(self._boxes)

    # TODO Implement validation for Box.yaml
    def _validate_boxes_format(self, boxes_dict):
        pass

    # TODO Implement validation for playground.yaml
    def _validate_template_format(self, template_dict):
        pass

    def _create_playground(self):
        playground = list()
        box_instances = self._create_box_instances_from(self._boxes)
        self._adjust_type_specific_parameters(box_instances)

        try:
            for template_component in self._template:
                box_instance = self._find_box_instance_by(template_component.get("name", None), box_instances)
                box_instance.software = self._create_software_instances_from(template_component)
                playground.append(box_instance)
        except store_exceptions.NotDefinedBoxException as exc:
            new_msg = "(In Template file, we found)" + exc.message
            raise store_exceptions.StoreManagerException(new_msg)
        except store_exceptions.ParameterNotFoundException as exc:
            raise store_exceptions.StoreManagerException(exc.message)

        return playground

    def _create_box_instances_from(self, box_dicts):
        box_instances = list()

        for b in box_dicts:
            box_instance = Box()
            try:
                box_instance.name = b["name"]
                box_instance.type = b["type"]
            except KeyError as exc:
                raise store_exceptions.ParameterNotFoundException("box.yaml", exc.args[0], None)

            box_instance.account = b.get("account", None)
            box_instance.setting = b.get("setting", dict())
            box_instance.setting["host_box"] = b.get("host_box", None)
            box_instance.network = self._create_nic_instance_list_from(b)
            box_instance.software = None
            box_instances.append(box_instance)
        return box_instances

    def _adjust_type_specific_parameters(self, box_instances):
        for box_instance in box_instances:
            box_type = box_instance.type
            if box_type == "physical":
                pass
            elif box_type == "virtual":
                host_box_instance = self._find_box_instance_by(box_instance.setting.get("host_box"), box_instances)
                box_instance.setting["host_box"] = host_box_instance
            elif box_type == "container":
                host_box_instance = self._find_box_instance_by(box_instance.setting.get("host_box"), box_instances)
                box_instance.setting["host_box"] = host_box_instance

    def _create_nic_instance_list_from(self, box_dict):
        nic_dicts = box_dict.get("network")

        if not nic_dicts:
            return None

        nic_instances = list()
        for n in nic_dicts:
            nic_instance = NetworkInterface()
            try:
                nic_instance.name = n["name"]
                nic_instance.ipaddr = n["ipaddr"]
                nic_instance.subnet = n["subnet"]
            except KeyError as exc:
                raise store_exceptions.ParameterNotFoundException("box.yaml",
                                                                "{}.{}".format(box_dict["name"], exc.args[0]),
                                                                  None)
            nic_instance.gateway = n.get("gateway", None)
            nic_instance.dns = n.get("dns", None)
            nic_instances.append(nic_instance)
        return nic_instances

    def _create_software_instances_from(self, template_component):
        software_dicts = template_component.get("software")

        if software_dicts is None:
            raise store_exceptions.ParameterNotFoundException("template.yaml",
                                                      "{}.{}".format(template_component.get("name", None), "software"),
                                                              None)

        software_instances = list()
        for software_dict in software_dicts:
            software_instance = Software()
            try:
                software_instance.name = software_dict["name"]
            except KeyError as exc:
                store_exceptions.ParameterNotFoundException("template.yaml",
                                                            "{}.{}".format(template_component.get("name", None), "software"),
                                                            None)
            software_instance.installer = software_dict.get("installer", None)
            software_instance.option = software_dict.get("opt", None)
            software_instance.version = software_dict.get("version", None)
            software_instances.append(software_instance)
        return software_instances

    def _find_box_instance_by(self, target_box_name, box_instances):
        for box in box_instances:
            if box.name == target_box_name:
                return box
        raise store_exceptions.NotDefinedBoxException(target_box_name)


if __name__ == "__main__":
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    print (pg)
