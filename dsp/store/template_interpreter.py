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
        self.initialize()

    def initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._store = StoreManager()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def get_playground(self):
        try:
            template_dict = self._get_template_dict()
            info_boxes_dict = self._get_boxes_dict()
        except store_exceptions.ParameterNotFoundException as exc:
            raise store_exceptions.TemplateInterpreterException(exc)

        playground_topology = list()

        for template_tenant in template_dict:
            for template_box in template_tenant["boxes"]:
                box_instance = None
                if template_box["type"] == "physical.box":
                    info_box_dict = self._get_box_from_boxes_dict(template_box["name"],
                                                                  template_box["where"],
                                                                  info_boxes_dict)
                    box_instance = self._create_pbox_instance(info_box_dict)

                elif template_box["type"] == "virtual.box":
                    box_instance = self._create_vbox_instance(template_box)

                box_instance.where = template_box["where"]
                box_instance.tenant = template_tenant["tenant"]
                box_instance.software = self._create_software_instances(template_box["software"])

                playground_topology.append(box_instance)

        self._logger.debug(playground_topology)
        return playground_topology

    def _get_template_dict(self):
        _template_dict = self._store.get_template()
        self._validate_template_format(_template_dict)
        return _template_dict

    def _get_boxes_dict(self):
        _boxes_dict = self._store.get_boxes()
        self._validate_boxes_format(_boxes_dict)
        return _boxes_dict

        # TODO Implement validation for Box.yaml
    def _validate_boxes_format(self, boxes_dict):
        pass

    def _create_vbox_instance(self, template_box):
        box_instance = Box()
        box_instance.name = template_box["name"]
        box_instance.type = template_box["type"]
        # box_instance.account = None
        # box_instance.network = None
        # box_instance.setting = None

        return box_instance

    def _create_pbox_instance(self, box_dict):
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

    def _create_nic_instance(self, nic_dict):
        nic_instance = NetworkInterface()

        # Required Parameters
        nic_instance.nic = nic_dict.get("nic", None)
        nic_instance.plane = nic_dict["plane"]
        nic_instance.ipaddr = nic_dict["ipaddr"]
        nic_instance.subnet = nic_dict["subnet"]

        # Optional Parameters
        nic_instance.gateway = nic_dict.get("gateway", None)
        nic_instance.dns = nic_dict.get("dns", None)

        return nic_instance

    # TODO Implement validation for playground.yaml
    def _validate_template_format(self, template_dict):
        pass

    def _get_box_from_boxes_dict(self, box_name, box_place, boxes_dict):
        where_dict = None
        for where in boxes_dict:
            if where["where"].lower() == box_place.lower():
                where_dict = where["boxes"]

        for box in where_dict:
            if box["name"].lower() == box_name.lower():
                return box

        return None

    def _create_software_instances(self, software_dicts):
        if len(software_dicts) == 0:
            return None

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


if __name__ == "__main__":
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    print(pg)
