# -*- coding: utf-8 -*-
from __future__ import print_function

import time
import logging
import yaml
import json
from multiprocessing import Process, Queue
import requests
from pprint import pprint
from typing import List

from abstracted_component.cluster import Cluster, ClusterJSONEncoder


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

    def compose(self, physical_topology, desired_playground):
        # self._in_parallel("reload", topology)
        return self._in_parallel("compose", physical_topology, desired_playground)

    def update(self, physical_topology, desired_playground):
        # self._in_parallel("reload", topology)
        return self._in_parallel("update", physical_topology, desired_playground)

    def release(self, physical_topology, desired_playground):
        # self._in_parallel("reload", topology)
        return self._in_parallel("release", physical_topology, desired_playground)

    def _in_parallel(self, mode, physical_topology: List[dict], desired_playground: List[Cluster]):
        procs = list()
        result_queue = Queue()

        for desired_cluster in desired_playground:
            proc = None

            # check the status of cluster posts
            # update boxes information
            # if mode == "reload":
            #     proc = Process(target=self._reload_cluster_description, args=(cluster, result_queue,))
            target_cluster_topology = None
            for c_topo in physical_topology:
                if c_topo["cluster"]["name"].lower() == desired_cluster.name.lower():
                    target_cluster_topology = c_topo
                    break

            if not target_cluster_topology:
                self._logger.warn("Error")
                return

            if mode == "compose":
                # proc = Process(target=self._compose_cluster, args=(desired_cluster, result_queue,))
                proc = Process(target=self._compose_cluster,
                               args=(target_cluster_topology, desired_cluster, result_queue))

            elif mode == "update":
                proc = Process(target=self._update_cluster, args=(desired_cluster, result_queue,))

            elif mode == "release":
                proc = Process(target=self._release_cluster, args=(desired_cluster, result_queue,))

            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

        return result_queue

    def _compose_cluster(self, cluster_topology: dict, cluster_desc: Cluster, result_queue: Queue):
        self._logger.debug("A New Installing Process Started. cluster: {}".format(cluster_desc.name))

        post_ip = cluster_topology["cluster"]["post"]["ipaddr"]
        post_port = cluster_topology["cluster"]["post"]["port"]

        req_msg = json.dumps(cluster_topology)
        self._logger.debug("HTTP Req Body: {}".format(cluster_topology))
        resp_msg = self.call_post_api("http://{}:{}/{}".format(post_ip, post_port, "topology"),
                                      "put",
                                      req_msg)
        result_queue.put([cluster_desc.name, resp_msg])

        req_msg = json.dumps(cluster_desc, cls=ClusterJSONEncoder)
        self._logger.debug("HTTP Req Body: {}".format(req_msg))
        resp_msg = self.call_post_api("http://{}:{}/{}".format(post_ip, post_port, "cluster"),
                                      'post',
                                      req_msg)
        self._logger.debug("A Process Finished. cluster: {}".format(resp_msg))

        result_queue.put([cluster_desc.name, resp_msg])

    def _update_cluster(self, cluster_desc: Cluster, result_queue: Queue) -> None:
        self._logger.debug("A New Process for updating a cluster is started. Cluster: {}".format(cluster_desc.name))

        # _post_interface: swagger_client.DspApi = swagger_client.DspApi(swagger_client.ApiClient())
        #
        # req_msg = json.dumps(cluster_desc)
        # self._logger.debug(req_msg)

        # resp_msg = _post_interface.dspupdate(req_msg)
        # self._logger.debug("The Process finished the update tasks. Cluster: {}".format(cluster_desc.name))
        # result_queue.put([cluster_desc.name, resp_msg])

    def _release_cluster(self, cluster_desc: Cluster, result_queue: Queue) -> None:
        self._logger.debug("A New Uninstalling Process Started. Box: {}".format(cluster_desc.name))
        # _post_interface: swagger_client.DspApi = swagger_client.DspApi(swagger_client.ApiClient())
        #
        # req_msg = json.dumps(cluster_desc)
        # self._logger.debug(req_msg)
        # resp_msg = _post_interface.dsprelease(req_msg)
        # self._logger.debug("A Process Finished. Box: {}".format(cluster_desc.name))
        # result_queue.put([cluster_desc.name, resp_msg])

    def call_post_api(self, url: str, method: str, message: str = None) -> str:
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        http_req = getattr(requests, method)
        response = http_req(url, data=message, headers=headers)

        return response

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
