# -*- coding: utf-8 -*-
import threading


class ProvisionCoordinator:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProvisionCoordinator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.prov_info = None

    def _prov_box(self, box_info):
        print "This thread will cover the provision of Box %s" % box_info.name
        for sw in box_info.sw:
            self._trigger_inst(sw_info=sw)
            pass

    def _trigger_inst(self, sw_info):
        pass

    def prov_playground(self, prov_info):
        threads = []
        for box in prov_info:
            t = threading.Thread(target=self._prov_box, args=(box,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
