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

    def showbox(self, box_info):
        print "This threads will cover a box %s" % box_info.name

    def prov_playground(self, prov_info):
        threads = []
        for box in prov_info:
            t = threading.Thread(target=self.showbox, args=(box,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
