# -*- coding: utf-8 -*-
import copy
import logging

from dsp.store.store_manager import StoreManager
from dsp.store import store_exceptions
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
        self._playground = None
        self.initialize()

    def initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._store = StoreManager()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def get_playground(self):
        try:
            box_instances = self._get_box_instances()
            self._boxes = self._fill_host_boxes(box_instances)
            template_dict = self._get_template()
            self._playground = self._put_template_to_box_instances(self._boxes, template_dict)
        except store_exceptions.ParameterNotFoundException as exc:
            raise store_exceptions.TemplateInterpreterException(exc)
        return self._playground

    def _get_box_instances(self):
        _boxes_dict = self._store.get_boxes()
        self._validate_boxes_format(_boxes_dict)
        box_instances = self._create_box_instances(_boxes_dict)

        return box_instances

    # TODO Implement validation for Box.yaml
    def _validate_boxes_format(self, boxes_dict):
        pass

    def _create_box_instances(self, boxes_dict):
        box_instances = list()

        for _box_dict in boxes_dict:
            _box_instance = self._create_box_instance(_box_dict)
            box_instances.append(_box_instance)

        return box_instances

    def _create_box_instance(self, box_dict):
        box_instance = Box()

        try:
            # Required Parameters
            box_instance.name = box_dict["name"]
            box_instance.type = box_dict["type"]
            box_instance.account = box_dict["account"]
            box_instance.network = self._create_nic_instances(box_dict["network"])
        except KeyError as exc:
            raise store_exceptions.ParameterNotFoundException("box.yaml", exc.args[0], None)

        # Optional Parameters
        box_instance.setting = box_dict.get("setting", dict())
        box_instance.setting["host_box"] = box_dict.get("host_box", None)

        return box_instance

    def _create_nic_instances(self, nics_dict):
        nic_instances = list()

        for nic_dict in nics_dict:
            nic_instance = self._create_nic_instance(nic_dict)
            nic_instances.append(nic_instance)

        return nic_instances

    @staticmethod
    def _create_nic_instance(nic_dict):
        nic_instance = NetworkInterface()

        # Required Parameters
        nic_instance.nic = nic_dict["nic"]
        nic_instance.type = nic_dict["type"]
        nic_instance.ipaddr = nic_dict["ipaddr"]
        nic_instance.subnet = nic_dict["subnet"]

        # Optional Parameters
        nic_instance.gateway = nic_dict.get("gateway", None)
        nic_instance.dns = nic_dict.get("dns", None)

        return nic_instance

    def _fill_host_boxes(self, box_instances):
        for box_instance in box_instances:
            box_type = box_instance.type
            if box_type == "virtual" or box_type == "container":
                host_box_name = box_instance.setting.get("host_box")
                host_box_instance = self._find_box_instance(host_box_name, box_instances)
                box_instance.setting["host_box"] = host_box_instance
        return box_instances

    def _get_template(self):
        _template_dict = self._store.get_template()
        self._validate_template_format(_template_dict)
        return _template_dict

    # TODO Implement validation for playground.yaml
    def _validate_template_format(self, template_dict):
        pass

    def _put_template_to_box_instances(self, box_instances, template_dict):
        playground = list()

        for template_component in template_dict:
            try:
                target_box_name = template_component["name"]
                copied_box_instance = copy.deepcopy(self._find_box_instance(target_box_name, box_instances))
                copied_box_instance.software = self._create_software_instances_from(template_component)
                playground.append(copied_box_instance)
            except KeyError as exc:
                raise store_exceptions.ParameterNotFoundException("template.yaml", exc.args[0], None)
            except store_exceptions.NotDefinedBoxException as exc:
                raise exc

        return playground

    @staticmethod
    def _create_software_instances_from(template_component):
        software_dicts = template_component["software"]
        software_instances = list()
        for software_dict in software_dicts:
            software_instance = Software()
            # Required Parameters
            software_instance.name = software_dict["name"]
            software_instance.installer = software_dict["installer"]
            # Optional Parameters
            software_instance.option = software_dict.get("opt", None)
            software_instance.version = software_dict.get("version", None)
            software_instances.append(software_instance)
        return software_instances

    @staticmethod
    def _find_box_instance(target_box_name, box_instances):
        for box in box_instances:
            if box.name == target_box_name:
                return box
        raise store_exceptions.NotDefinedBoxException(target_box_name)


if __name__ == "__main__":
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    print(pg)
