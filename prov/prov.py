# -*- coding: utf-8 -*-
import threading
import logging


class ProvisionCoordinator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProvisionCoordinator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._prov_info = None

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def _prov_box(self, box_info):
        self._logger.debug('This Thread will cover the provision of Box %s', box_info.name)
        for sw in box_info.sw:
            self._trigger_inst(sw_info=sw)

    def _trigger_inst(self, sw_info):
        self._logger.debug("Start the installer %s", sw_info.name)

        if "ansible" in sw_info.name:
            self._logger.debug("Install Software with Ansible")
        else:
            self._logger.debug("Install Software without Ansible")

    def prov_playground(self, prov_info):
        threads = []
        self._prov_info = prov_info
        for box in self._prov_info:
            t = threading.Thread(target=self._prov_box, args=(box,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
