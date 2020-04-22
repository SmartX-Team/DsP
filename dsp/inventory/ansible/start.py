import os
import yaml
import json
import logging
import subprocess
import datetime
from dsp.abstracted_component.inst_tool_iface import InstallationToolInterface
from dsp.inventory.inventory_exceptions import *


class AnsibleInterface(InstallationToolInterface):
    def __init__(self):
        super(AnsibleInterface, self).__init__()
        self.name = str
        self.software_list = None
        self.inventory_config = None
        self.playbook_config = None

        self._logger = logging.getLogger(self.__class__.__name__)
        self.initialize()
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def initialize(self, _setting_file="setting.yaml"):
        _file_path = os.path.join(os.path.dirname(__file__), _setting_file)

        with open(_file_path, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr, Loader=yaml.FullLoader)

        self.name = fy["name"]
        self.software_list = fy["target_software"]
        self.inventory_config = fy["config"].get("inventory")
        self.playbook_config = fy["config"].get("playbook")

    def install(self, box_desc, target_software):
        tstart = datetime.datetime.now()

        # ansible-playbook -i <inventory_file> -l <hostname or groupname> <playbook>

        ansible_cmd = None

        if box_desc.type == "virtual.box":
            if box_desc.where == "post":
                ansible_cmd = self._get_vbox_install_command(box_desc, target_software)
        elif box_desc.type == "physical.box":
            try:
                ansible_cmd = self._get_pbox_install_command(box_desc, target_software)
            except KeyError as err:
                raise InstallerParameterNotExistException(self.name, err.args[0])
            except subprocess.CalledProcessError as err:
                error_msg = ("Box: {}, Command: {}".format(ansible_cmd.hn, err.cmd) +
                             "Error: {}".format(err.output))
                raise InstallerFailException(self.name, error_msg)

        self._logger.debug("Ansible command: {}".format(ansible_cmd.get_command()))
        res = ansible_cmd.execute()
        self._logger.debug("The provisioning result of Ansible: {}".format(res))

        tend = datetime.datetime.now()
        elasped_time = (tend - tstart).total_seconds()

        result_msg = "Installation Complete. Box: {}, Software: {}, Elasped Time: {}".format(box_desc.name,
                                                                                             target_software.name,
                                                                                             elasped_time)
        return result_msg

    def _get_vbox_install_command(self, box_desc, sw_desc):
        inventory_file = None
        playbook_file = "{}/{}/{}".format(self.playbook_config["root_dir"],
                                          sw_desc.name,
                                          self.playbook_config[sw_desc.name]["install"])

        cmd = self.AnsibleCommand()
        cmd.add_inventory(inventory_file)
        cmd.add_playbook(playbook_file)
        cmd.add_extra_vars("tenant", box_desc.tenant)
        cmd.add_extra_vars("vbox_name", box_desc.name)

        vbox_options = sw_desc.option
        for k in vbox_options.keys():
            cmd.add_extra_vars(k, vbox_options.get(k))

        return cmd

    def _get_pbox_install_command(self, box_desc, target_software):
        # cmd.hostname(box_desc.name)

        # sw_name = target_software.name
        inventory_filepath = "{}/{}".format(self.inventory_config["root_dir"], box_desc.name.lower())
        playbook_filepath = "{}/{}".format(self.playbook_config["root_dir"], target_software.name)

        software_type = target_software.option.get("type", None)
        if software_type:
            playbook_filepath = "{}/{}/{}".format(playbook_filepath,
                                                target_software.option["type"],
                                                self.playbook_config[target_software.name][software_type]["install"])
        else:
            playbook_filepath = "{}/{}".format(playbook_filepath,
                                            self.playbook_config[target_software.name][software_type]["install"])

        cmd = self.AnsibleCommand()
        cmd.add_inventory(inventory_filepath)
        cmd.add_playbook(playbook_filepath)

        return cmd

    def _create_ansible_command(self, inventory, playbook):
        cmd = self.AnsibleCommand()
        cmd.add_inventory(inventory)
        cmd.add_playbook(playbook)

        return cmd

    def uninstall(self, box_desc, target_software):
        tstart = datetime.datetime.now()

        # ansible-playbook -i <inventory_file> -l <hostname or groupname> <playbook>

        ansible_cmd = None

        if box_desc.type == "virtual.box":
            if box_desc.where == "post":
                ansible_cmd = self._get_vbox_uninstall_command(box_desc, target_software)
        elif box_desc.type == "physical.box":
            try:
                ansible_cmd = self._get_pbox_uninstall_command(box_desc, target_software)
            except KeyError as err:
                raise InstallerParameterNotExistException(self.name, err.args[0])
            except subprocess.CalledProcessError as err:
                error_msg = ("Box: {}, Command: {}".format(ansible_cmd.hn, err.cmd) +
                             "Error: {}".format(err.output))
                raise InstallerFailException(self.name, error_msg)

        self._logger.debug("Ansible command: {}".format(ansible_cmd.get_command()))
        res = ansible_cmd.execute()
        self._logger.debug("The provisioning result of Ansible: {}".format(res))

        tend = datetime.datetime.now()
        elasped_time = (tend - tstart).total_seconds()

        result_msg = "Uninstallation Complete. Box: {}, Software: {}, Elasped Time: {}".format(box_desc.name,
                                                                                               target_software.name,
                                                                                               elasped_time)
        return result_msg

    def _get_vbox_uninstall_command(self, box_desc, target_software):
        inventory_file = None
        playbook_file = "{}/{}/{}".format(self.playbook_config["root_dir"],
                                          target_software.name,
                                          self.playbook_config[target_software.name]["uninstall"])
        cmd = self.AnsibleCommand()
        cmd.add_inventory(inventory_file)
        cmd.add_playbook(playbook_file)
        cmd.add_extra_vars("tenant", box_desc.tenant)
        cmd.add_extra_vars("vbox_name", box_desc.name)

        vbox_options = target_software.option
        for k in vbox_options.keys():
            cmd.add_extra_vars(k, vbox_options.get(k))

        return cmd

    def _get_pbox_uninstall_command(self, box_desc, target_software):
        # sw_name = target_software.name
        inventory_file = "{}/{}".format(self.inventory_config["root_dir"], box_desc.name.lower())
        playground_file = "{}/{}".format(self.playbook_config["root_dir"], target_software.name)

        software_type = target_software.option.get("type", None)
        if software_type:
            playground_file = "{}/{}/{}".format(playground_file,
                                                target_software.option["type"],
                                                self.playbook_config[target_software.name][software_type]["uninstall"])
        else:
            playground_file = "{}/{}".format(playground_file,
                                            self.playbook_config[target_software.name][software_type]["uninstall"])

        ansible_command = self._create_ansible_command(inventory_file, playground_file)
        return ansible_command

    def update(self, box_desc, target_software):
        pass

    def check_tool_status(self):
        pass

    class AnsibleCommand:
        def __init__(self):
            self.iv = None
            self.hn = None
            self.pb = None
            self.ev = dict()

        def add_inventory(self, _inventory):
            self.iv = _inventory

        def add_hostname(self, _hostname):
            self.hn = _hostname

        def add_playbook(self, _playbook):
            self.pb = _playbook

        def add_extra_vars(self, _key, _value):
            self.ev[_key] = _value

        def execute(self):
            cmd = self.get_command()
            p = subprocess.Popen(cmd.__str__(),
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True)
            _, msg = p.communicate()

            return msg

        def get_command(self):
            cmd = "ansible-playbook"
            if self.iv:
                cmd = "{} {} {}".format(cmd, "-i", self.iv)

            if self.hn:
                cmd = "{} {} {}".format(cmd, "-l", self.hn)

            if len(self.ev) is not 0:
                ext_vars = json.dumps(self.ev)
                cmd = "{} {} \'{}\'".format(cmd, "--extra-vars", ext_vars)

            if self.pb:
                cmd = "{} {}".format(cmd, self.pb)
            else:
                raise InstallerParameterNotExistException("AnsibleInstaller", "playbook")

            return cmd
