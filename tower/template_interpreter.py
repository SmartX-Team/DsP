# -*- coding: utf-8 -*-
import logging
from typing import List

from tower.store.store_manager import StoreManager
from tower.store import store_exceptions
from abstracted_component.box import Box, NetworkInterface
from abstracted_component.software import Software
from abstracted_component.cluster import Cluster
from abstracted_component.function import Function


class TemplateInterpreter:
    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._store: StoreManager = StoreManager()
        self._logger: logging = logging.getLogger(self.__class__.__name__)

    def get_physical_topology(self):
        clusters_desc = self._store.get_file_dict("box.yaml")
        self._validate_boxes_format(clusters_desc)

        cluster_instances = list()

        for cluster_desc in clusters_desc:
            cluster_instance = Cluster()
            cluster_instance.name = cluster_desc["cluster"]["name"]
            cluster_instance.boxes = list()

            for box_desc in cluster_desc["cluster"]["boxes"]:
                box_instance = Box()
                box_instance.name = box_desc["name"]
                box_instance.where = cluster_instance.name
                box_instance.tenant = None
                box_instance.type = box_desc["type"]
                box_instance.account = box_desc["account"]
                box_instance.network = box_desc["network"]
                box_instance.setting = None
                box_instance.software = None
                cluster_instance.boxes.append(box_instance)

            cluster_instances.append(cluster_instance)

        return cluster_instances

    def get_playground(self):
        self._logger.debug("Start loading playground template from the store")

        # Loading files to dictionary instances
        try:
            template_dict = self._store.get_file_dict("playground.yaml")
            self._validate_template_format(template_dict)

            info_boxes_dict = self._store.get_file_dict("box.yaml")
            self._validate_boxes_format(info_boxes_dict)

        except store_exceptions.ParameterNotFoundException as exc:
            raise store_exceptions.TemplateInterpreterException(exc)
        self._logger.debug("Finish loading playground template")

        # Transforming the dictionary to instances
        clusters_instances = list()
        boxes_instances = list()
        functions_instances = list()

        self._logger.debug("Start interpreting playground template")

        for tenant_desc in template_dict:
            tenant_boxes_desc = tenant_desc.get("boxes")
            tenant_functions_desc = tenant_desc.get("functions")

            # Init cluster instances from template
            self._init_clusters_desc(clusters_instances, tenant_boxes_desc)
            self._init_clusters_desc(clusters_instances, tenant_functions_desc)

            # Init box instances from template
            self._init_boxes_desc(boxes_instances, tenant_boxes_desc)

            # Init function instances from template
            self._init_funcions_desc(functions_instances, tenant_functions_desc)

            # Fill box instances with additional information
            self._fill_boxes_inst(boxes_instances, info_boxes_dict, tenant_desc["tenant"])

            # Fill function instances with additional information
            self._fill_func_insts(functions_instances, tenant_desc["tenant"])

            # Append box instances to cluster's list
            self._match_box_to_cluster(clusters_instances, boxes_instances)

            # Append function instances to cluster's list
            self._match_func_to_cluster(clusters_instances, functions_instances)

        self._logger.debug("Finish interpreting playground template")
        self._logger.debug(clusters_instances)
        return clusters_instances

    def _init_clusters_desc(self, all_cluster_list: List[Cluster], elem_descs: List[dict]) -> None:
        for _elem_desc in elem_descs:
            _cluster_name = _elem_desc["where"].split(".")[0]

            if not self._find_by_name(all_cluster_list, "name", _cluster_name):
                _cluster_desc = Cluster()
                _cluster_desc.name = _cluster_name
                _cluster_desc.boxes = None
                _cluster_desc.functions = None

                all_cluster_list.append(_cluster_desc)

    def _init_boxes_desc(self, all_boxes_list: List[Box], tenant_boxes_desc: List[dict]) -> None:
        for box_desc in tenant_boxes_desc:
            if not self._find_by_name(all_boxes_list, "name", box_desc["name"]):
                _box_instance = Box()
                _box_instance.name = box_desc["name"]
                _box_instance.where = box_desc["where"]
                _box_instance.type = box_desc["type"]
                _box_instance.setting = box_desc.get("setting")
                _box_instance.software = self._create_software_instances(box_desc["software"])

                all_boxes_list.append(_box_instance)

    def _init_funcions_desc(self, all_func_list: List[Function], tenant_functions_desc: List[dict]) -> None:
        for func_desc in tenant_functions_desc:
            if not self._find_by_name(all_func_list, "name", func_desc["name"]):
                _function_instance = Function()
                _function_instance.name = func_desc["name"]
                _function_instance.where = func_desc["where"]
                _function_instance.type = func_desc["type"]
                _function_instance.installer = func_desc["installer"]
                _function_instance.option = func_desc.get("option")

                all_func_list.append(_function_instance)

    def _fill_func_insts(self, all_func_list: List[Function], tenant: str) -> None:
        for _func_inst in all_func_list:
            _func_inst.tenant = tenant

    def _fill_boxes_inst(self, all_boxes_list: List[Box], boxes_spec: List[dict], tenant: str) -> None:
        for _box_inst in all_boxes_list:
            _box_inst.tenant = tenant

            box_spec = None
            for _c in boxes_spec:
                box_spec = self._find_by_name(_c["cluster"]["boxes"], "name", _box_inst.name)
                if box_spec:
                    break

            if box_spec:
                _box_inst.account = box_spec.get("account")
                _box_inst.network = self._create_nic_instances(box_spec.get("network"))
            else:
                _box_inst.account = None
                _box_inst.network = None

    def _match_func_to_cluster(self, all_clusters_list, all_func_list):
        for _func_inst in all_func_list:
            _cluster_name = _func_inst.where.split(".")[0]
            _cluster_inst: Cluster = self._find_by_name(all_clusters_list, "name", _cluster_name)

            if _cluster_inst:
                if not _cluster_inst.functions:
                    _cluster_inst.functions = list()
                _cluster_inst.functions.append(_func_inst)

    def _match_box_to_cluster(self, all_cluster_list, all_boxes_list):
        for _box_inst in all_boxes_list:
            _cluster_name = _box_inst.where.split(".")[0]
            _cluster_inst: Cluster = self._find_by_name(all_cluster_list, "name", _cluster_name)

            if _cluster_inst:
                if not _cluster_inst.boxes:
                    _cluster_inst.boxes = list()
                _cluster_inst.boxes.append(_box_inst)

    def _find_by_name(self, source_list, field, value):
        for e in source_list:
            if isinstance(e, dict):
                if e.get(field).lower() == value.lower():
                    return e
            else:
                if getattr(e, field).lower() == value.lower():
                    return e

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
            software_instance.option = software_dict.get("option", None)
            software_instance.version = software_dict.get("version", None)
            software_instances.append(software_instance)
        return software_instances


if __name__ == "__main__":
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    print(pg)
