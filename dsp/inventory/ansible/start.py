import os
import yaml
import logging
import subprocess
from dsp.abstracted_component.installer import Installer
from dsp.inventory.inventory_exceptions import *


class AnsibleInstaller(Installer):

    def __init__(self):
        super(AnsibleInstaller, self).__init__()
        self.name = "AnsibleInstaller"
        self.installable_software = None
        self._root_dir = str
        self._default_inventory = str
        self._playbook_mapping = None

        self._logger = logging.getLogger(self.__class__.__name__)
        self.initialize()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def initialize(self, _setting_file="setting.yaml"):
        _file_path = os.path.join(os.path.dirname(__file__), _setting_file)
        with open(_file_path, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr)
        self.name = fy["name"]
        self.installable_software = fy["target_software"]
        self._root_dir = fy["root_directory"]
        self._default_inventory = fy.get("default_inventory")
        self._playbook_mapping = fy["config"]["playbook_mapping"]

    def install(self, box_desc, target_software):
        # ansible-playbook -i <inventory_file> -l <hostname or groupname> <playbook>
        cmd = None
        try:
            cmd = self._create_ansible_command(box_desc, target_software)
            self._execute_command(cmd)
        except KeyError as err:
            raise InstallerParameterNotExistException(self.name, err.args[0])
        except subprocess.CalledProcessError as err:
            error_msg = ("Box: {}, Command: {}".format(cmd.hn, err.cmd) +
                         "Error: {}".format(err.output))
            InstallerFailException(self.name, error_msg)

    def uninstall(self, box_desc, target_software):
        pass

    def update(self, box_desc, target_software):
        pass

    def check_status(self):
        pass

    def _create_ansible_command(self, box_desc, target_software, exec_type):
        cmd = AnsibleCommand()

        cmd.hostname(box_desc.name)

        sw_name = target_software.name
        sw_ver = target_software.version
        sw_type = target_software.option["type"]
        playbook_name = self._playbook_mapping[sw_name][sw_ver][sw_type][exec_type]
        cmd.playbook(playbook_name)

        if target_software.option("inventory"):
            cmd.inventory(target_software.option("inventory"))
        else:
            cmd.inventory(self._default_inventory)

        return cmd

    def _execute_command(self, cmd):
        subprocess.run(cmd.__str__(),
                       stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       shell=True, check=True)


class AnsibleCommand:
    def __init__(self):
        self.iv = str
        self.hn = str
        self.pb = str

    def inventory(self, _inventory):
        self.iv = _inventory

    def hostname(self, _hostname):
        self.hn = _hostname

    def playbook(self, _playbook):
        self.pb = _playbook

    def __str__(self):
        cmd = "ansible"
        if self.iv:
            cmd = "{} {} {}".format(cmd, "-i", self.iv)
        if self.hn:
            cmd = "{} {} {}".format(cmd, "-l", self.hn)
        if self.pb:
            cmd = "{} {}".format(cmd, self.pb)
        else:
            raise InstallerParameterNotExistException("AnsibleInstaller", "playbook")
        return cmd
