import os
import logging
import yaml
import interface
from dsp.abstracted_component.installer import Installer


class MAASInstaller(Installer):

    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MAASInstaller, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super(MAASInstaller, self).__init__()
        self.interface = None
        self.setting = None

        self._logger = None
        self._initialize_logger()

    def _initialize_logger(self):
        self._logger = logging.getLogger("DsP")
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self._logger.addHandler(sh)

    def initialize(self, _setting_file="setting.yaml"):
        self._load_maas_setting(_setting_file)
        self._create_maas_interface()

    def _load_maas_setting(self, _setting_file):
        p = os.path.abspath(os.getcwd()) + "/" + _setting_file
        self.setting = self._read_yaml_file(p)

    def _create_maas_interface(self):
        maas_ip = self.setting['config']['maas_ip']
        apikey = self.setting['config']['apikey']
        self.interface = interface.MaasInterface(maas_ip, apikey)

    def install(self, playground):
        pass

    def uninstall(self, playground):
        pass

    def update(self, playground):
        pass

    def check_status(self):
        pass

    def start(self, __params_str):
        _params = yaml.load(__params_str)
        for box_param in _params:
            self._provisioning_machine(box_param)

    def _provisioning_machine(self, __params):

        _hostname = __params['hostname']
        _dist = __params['image']['dist']
        _version = __params['image']['version']

        machine = self.interface.get_machine_by(_hostname)

        if not machine:
            return
        if _dist == u'ubuntu':
            _dist = self._ubuntu_distro_mapping(_version)
        elif _dist == u'centos':
            _dist = _dist+_version
        else:
            _dist = None
        self.interface.deploy_machine_by(_hostname, _dist)

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

    def _read_yaml_file(self, _file):
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
                    return None

if __name__ == "__main__":
    maas = MAASInstaller()
    maas.initialize()

    _p = os.path.abspath(os.getcwd()) + "/example.yaml"
    _fp = open(_p, mode='r')
    maas.start(_fp.read())