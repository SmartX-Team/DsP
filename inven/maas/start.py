import os
import logging
import yaml
import inven.maas.interface as maas_iface


class MaasSupervisor:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MaasSupervisor, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.maasif = None
        self.setting = None

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def initialize(self, __cfgfile="/agent.yaml"):
        p = os.path.abspath(os.getcwd()) + __cfgfile
        fp = open(p, mode='r')
        self.setting = yaml.load(fp.read())['config']
        self.maasif = maas_iface.MaasInterface()
        self.maasif.initizilize(
            "http://"+self.setting['maas_ip'] + "/MAAS/api/2.0/",
            self.setting['apikey'])
        fp.close()

    def start(self, __params_str):
        _params = yaml.load(__params_str)
        for box_param in _params:
            self._provisioning_machine(box_param)

    def _provisioning_machine(self, __params):

        _hostname = __params['hostname']
        _dist = __params['image']['dist']
        _version = __params['image']['version']

        machine = self.maasif.get_machine(_hostname)

        if not machine:
            return
        if _dist == u'ubuntu':
            _dist = self._ubuntu_distro_mapping(_version)
        elif _dist == u'centos':
            _dist = _dist+_version
        else:
            _dist = None
        self.maasif.deploy_machine(_hostname, _dist)

    def _ubuntu_distro_mapping(self, __dist):
        if "14.04" in __dist:
            return 'trusty'
        elif "14.10" in __dist:
            return 'unicorn'
        elif "15.04" in __dist:
            return 'vervet'
        elif "15.10" in __dist:
            return 'werewolf'
        elif "16.04" in __dist:
            return 'xenial'
        elif "16.10" in __dist:
            return 'yak'
        elif "17.04" in __dist:
            return 'zapus'
        else:
            return __dist

if __name__ == "__main__":
    maas = MaasSupervisor()
    maas.initialize()

    _p = os.path.abspath(os.getcwd()) + "/example.yaml"
    _fp = open(_p, mode='r')
    maas.start(_fp.read())