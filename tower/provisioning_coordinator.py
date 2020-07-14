# -*- coding: utf-8 -*-
from __future__ import print_function

import time
import logging
import yaml
import json
from multiprocessing import Process, Queue, Lock
from pprint import pprint

from abstracted_component.cluster import Cluster, ClusterJSONEncoder

from tower.post_interface import swagger_client
from swagger_client.rest import ApiException


class ProvisionCoordinator(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProvisionCoordinator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._logger: logging = None
        self._playground = None
        self._initialize_logger()

    def _initialize_logger(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.setLevel(logging.DEBUG)
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def compose(self, playground):
        return self._execute_coordination("compose", playground)

    def release(self, playground):
        return self._execute_coordination("release", playground)

    def _execute_coordination(self, mode, playground):
        procs = list()
        result_queue = Queue()

        for cluster in playground:
            proc = None
            if mode == "compose":
                proc = Process(target=self._compose_cluster, args=(cluster, result_queue,))

            elif mode == "release":
                proc = Process(target=self._release_cluster, args=(cluster, result_queue,))

            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

        return result_queue

    def _compose_cluster(self, cluster_desc: Cluster, result_queue: Queue) -> None:
        self._logger.debug("A New Installing Process Started. cluster: {}".format(cluster_desc.name))

        _post_interface: swagger_client.DspApi = swagger_client.DspApi(swagger_client.ApiClient())

        req_msg = json.dumps(cluster_desc, cls=ClusterJSONEncoder)
        self._logger.debug("HTTP Req Body: {}".format(req_msg))
        c = json.loads(req_msg, object_hook=Cluster.json_decode)
        pprint(c)
        # resp_msg = _post_interface.dspcompose(req_msg)
        # self._logger.debug("A Process Finished. cluster: {}".format(cluster_desc.name))
        # result_queue.put([cluster_desc.name, resp_msg])

    def _release_cluster(self, cluster_desc: Cluster, result_queue: Queue) -> None:
        self._logger.debug("A New Uninstalling Process Started. Box: {}".format(cluster_desc.name))

        _post_interface: swagger_client.DspApi = swagger_client.DspApi(swagger_client.ApiClient())

        req_msg = json.dumps(cluster_desc)
        self._logger.debug(req_msg)
        # resp_msg = _post_interface.dsprelease(req_msg)
        # self._logger.debug("A Process Finished. Box: {}".format(cluster_desc.name))
        # result_queue.put([cluster_desc.name, resp_msg])

    def _read_yaml_file(self, _file: str) -> dict or Exception:
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
                    raise ValueError(exc)
