import os
import logging
import yaml
import datetime
from dsp.abstracted_component.inst_tool_iface import InstallationToolInterface
from dsp.inventory import inventory_exceptions
from maas import client as maas_client
from maas.client.enum import NodeStatus


class MAASInterface(InstallationToolInterface):
    # For singleton design
    _instance = None
    _maas_interface = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MAASInterface, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super(MAASInterface, self).__init__()
        # Variables for Interface Description
        self.name = str
        self.version = str
        self.software = list
        self._setting = dict

        self._maas_url = str
        self._maas_apikey = str

        self._logger = logging.getLogger(self.__class__.__name__)
        self.initialize()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

        MAASInterface._maas_interface = maas_client.connect(self._maas_url, apikey=self._maas_apikey)

    def initialize(self, _setting_file="setting.yaml"):
        _file_path = os.path.join(os.path.dirname(__file__), _setting_file)
        with open(_file_path, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr, Loader=yaml.FullLoader)

        self._load_installer_setting(fy)
        self._load_maas_setting(self._setting["maas"])

    def _load_installer_setting(self, fy):
        self.name = fy["name"]
        self.software = fy["target_software"]
        self._setting = fy["config"]

    def _load_maas_setting(self, maas_cfg):
        self._maas_url = "http://{}:{}/MAAS/".format(maas_cfg['maas_ip'], maas_cfg['maas_port'])
        self._maas_apikey = maas_cfg['apikey']

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
        tstart = datetime.datetime.now()

        maas_desc = target_software
        machine = self._get_machine(box_desc.name)
        # self._logger.debug(yaml.dump(box_desc))

        res = None
        if machine.status == NodeStatus.READY:
            linux_ver = None
            if maas_desc:
                linux_ver = maas_desc.option.get("version", "xenial")
            self._logger.info("Install Linux {} to {}".format(linux_ver, box_desc.name))
            res = "Installation Complete."
            machine.deploy(wait=True, distro_series=linux_ver)
        else:
            res = "Machine is not ready for install (Status: {}).".format(machine.status_name)

        tend = datetime.datetime.now()
        elasped_time = (tend - tstart).total_seconds()

        result_msg = "Software: {}, Elasped Time: {}. {}".format(maas_desc.name,
                                                                 elasped_time,
                                                                 res)
        return result_msg

    def uninstall(self, box_desc, mass_desc):
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
        tstart = datetime.datetime.now()


        if not mass_desc.name == "linux":
            raise inventory_exceptions.InstallerFailException(self.name,
                                                              "Uninstalling {} is not supported".format(
                                                                  mass_desc["name"]))

        res = None

        machine = self._get_machine(box_desc.name)
        if machine.status in [NodeStatus.DEPLOYED, NodeStatus.FAILED_DEPLOYMENT]:
            machine.release(wait=True, erase=True, secure_erase=True)
            res = "Uninstalling pBox is successfully completed."

        else:
            res = "Machine is not ready for uninstallation (Status: {}).".format(machine.status_name)

        tend = datetime.datetime.now()
        elasped_time = (tend - tstart).total_seconds()

        result_msg = "Software: {}, Elasped Time: {}. {}".format(mass_desc.name,
                                                                 elasped_time,
                                                                 res)
        return result_msg

    def update(self, box_desc, target_software):
        pass

    def check_tool_status(self):
        pass

    def _get_machine(self, hostname):
        self._logger.debug(self._maas_url)
        self._logger.debug(self._maas_apikey)

        machine_list = MAASInterface._maas_interface.machines.list()
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
    maas = MAASInterface()

    p = os.path.abspath(os.getcwd()) + "/" + "setting.yaml"
    with open(p, 'r') as stream:
        with open(p, mode='r') as f:
            setting_str = f.read(-1)
        setting = yaml.load(setting_str, Loader=yaml.FullLoader)
    maas.initialize(setting)

    from dsp.store.template_interpreter import TemplateInterpreter
    interp = TemplateInterpreter()
    pg = interp.get_playground()
    for box_with_sws in pg:
        for sw in box_with_sws["software"]:
            if sw["installer"] is "maas":
                maas.install(box_with_sws, sw)
