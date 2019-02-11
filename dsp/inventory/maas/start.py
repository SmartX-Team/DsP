import os
import logging
import yaml
from dsp.abstracted_component.installer import Installer
from dsp.inventory import inventory_exceptions
from maas import client as maas_client
from maas.client.enum import NodeStatus


class MAASInstaller(Installer):
    # For singleton design
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MAASInstaller, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super(MAASInstaller, self).__init__()
        self.name = str
        self.version = str
        self.software = list
        self._setting = dict
        self._interface = None

        self._logger = logging.getLogger(self.__class__.__name__)
        self.initialize()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def initialize(self, _setting_file="setting.yaml"):
        _file_path = os.path.join(os.path.dirname(__file__), _setting_file)
        with open(_file_path, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr)
        self.name = fy["name"]
        self.software = fy["target_software"]
        self._setting = fy["config"]

        self._create_maas_interface()

    def _load_maas_setting(self, _setting_file):
        p = os.path.abspath(os.getcwd()) + "/" + _setting_file
        if os.path.isfile(p):
            self._setting = self._read_yaml_file(p)
        else:
            raise inventory_exceptions.InstallerException("{}: Setting file is not exists".format(self.name))

    def _create_maas_interface(self):
        maas_ip = self._setting['maas_ip']
        maas_port = self._setting['maas_port']
        maas_url = "http://{}:{}/MAAS/".format(maas_ip, maas_port)

        apikey = self._setting['apikey']
        # Todo Creating MAAS Instance with ID/PW
        self._interface = maas_client.connect(maas_url, apikey=apikey)

    def install(self, box_desc, target_software):
        """Deploy this machine.

        :param user_data: User-data to provide to the machine when booting. If
            provided as a byte string, it will be base-64 encoded prior to
            transmission. If provided as a Unicode string it will be assumed
            to be already base-64 encoded.
        :param distro_series: The OS to deploy.
        :param hwe_kernel: The HWE kernel to deploy. Probably only relevant
            when deploying Ubuntu.
        :param comment: A comment for the event log.
        :param wait: If specified, wait until the deploy is complete.
        :param wait_interval: How often to poll, defaults to 5 seconds
        """
        maas_desc = target_software
        machine = self._get_machine(box_desc.name)
        self._logger.debug(yaml.dump(box_desc))

        if machine.status in [NodeStatus.DEPLOYED, NodeStatus.DEPLOYING]:
            machine.release(wait=True)

        if machine.status == NodeStatus.READY:
            linux_ver = None
            if maas_desc:
                linux_ver = maas_desc.option.get("version", None)
            machine.deploy(wait=True, distro_series=linux_ver)
        else:
            inventory_exceptions.InstallerFailException(self.name,
                                                        "Machine is not ready for install. Status: {}".
                                                        format(machine.status_name))

    def uninstall(self, box_desc, target_software):
        """
        Release the machine.

        :param comment: Reason machine was released.
        :type comment: `str`
        :param erase: Erase the disk when release.
        :type erase: `bool`
        :param secure_erase: Use the drive's secure erase feature if available.
        :type secure_erase: `bool`
        :param quick_erase: Wipe the just the beginning and end of the disk.
            This is not secure.
        :param wait: If specified, wait until the deploy is complete.
        :type wait: `bool`
        :param wait_interval: How often to poll, defaults to 5 seconds.
        :type wait_interval: `int`
        """
        box_name = box_desc.name
        sw_opt = box_desc.opt
        machine = self._get_machine(box_desc['name'])

        if machine.status == NodeStatus.DEPLOYED:
            machine.release(wait=True)
        elif machine.status == NodeStatus.READY:
            pass
        else:
            inventory_exceptions.InstallerFailException(self.name,
                                                        "Machine is not ready for uninstall. Status: {}".
                                                        format(machine.status_name))

    def update(self, box_desc, target_software):
        pass

    def check_status(self):
        if self._interface:
            return self.InstallerStatus.Available
        else:
            return self.InstallerStatus.Fail

    def _get_machine(self, hostname):
        machine_list = self._interface.machines.list()
        for m in machine_list:
            if m.hostname == hostname:
                self._logger.debug("{} {}".format(m.hostname, m.architecture))
                return m
        # Available Varilabes in Machine
        # block_devices, boot_interface, cpus, disable_ipv4, fqdn, hostname, hwe_kernel, interfaces, ip_addresses,
        # loaded, memory, node_type, osystem, owner, power_type, power_state, status, status_name, system_id, tags,
        # volume_groups

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
    logging.basicConfig(format="[%(asctime)s / %(levelname)s] %(filename)s,%(funcName)s(#%(lineno)d): %(message)s",
                        level=logging.DEBUG)
    maas = MAASInstaller()

    p = os.path.abspath(os.getcwd()) + "/" + "setting.yaml"
    with open(p, 'r') as stream:
        with open(p, mode='r') as f:
            setting_str = f.read(-1)
        setting = yaml.load(setting_str)
    maas.initialize(setting)

    from dsp.store.template_interpreter import TemplateInterpreter
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    for box_with_sws in pg:
        maas.install(box_with_sws)
