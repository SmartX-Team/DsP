import os
import logging

import yaml
import inven.ubuntu.interface as maas_iface


class MaasSupervisor:
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MaasSupervisor, cls).__new__(cls)
        return cls._instance

    def __init__(self, __cfgfile):
        self.maasif = None
        self.setting = None

        if __cfgfile:
            self.initialize(__cfgfile)

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        return

    def initialize(self, __cfgfile="setting.yaml"):
        p = os.path.abspath(os.getcwd()) + __cfgfile
        fp = open(p, mode='r')
        self.setting = yaml.load(fp.read())['config']
        self.maasif = maas_iface.MaasInterface(self.setting['apikey'])
        fp.close()

    def start(self, __params):
        params = yaml.load(__params)
        return


if __name__ == "__main__":
    maas = MaasSupervisor()
    p = os.path.abspath(os.getcwd()) + "/setting.yaml"
    maas.start()
