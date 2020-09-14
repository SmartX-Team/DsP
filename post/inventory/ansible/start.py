import os
import yaml
import json
import logging
import subprocess
import datetime
from abstracted_component.inst_tool_iface import InstallationToolInterface

from abstracted_component.box import Box
from abstracted_component.software import Software
from abstracted_component.function import Function


class AnsibleInterface(InstallationToolInterface):
    name_prefix = "ansible"

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

    def install(self, box_desc: Box, target_software: Software or Function):
        tstart = datetime.datetime.now()

        ansible_cmd = None

        _inven_str = self._generate_ansible_inventory(box_desc)
        _inven_filepath = self._create_temp_inventory(_inven_str, "{}.yaml".format(box_desc.name))

        if isinstance(target_software, Software):
            # Box Provisioning
            if box_desc.type == "virtual.box":
                if box_desc.where == "post":
                    ansible_cmd = self._get_vbox_install_command(box_desc, target_software, _inven_filepath)
            elif box_desc.type == "physical.box":
                ansible_cmd = self._get_pbox_install_command(box_desc, target_software, _inven_filepath)

        elif isinstance(target_software, Function):
            ansible_cmd = self._get_func_install_command(target_software, _inven_filepath)

        else:
            return

        # ansible-playbook -i <inventory_file> -l <hostname or groupname> <playbook>
        self._logger.debug("Ansible command: {}".format(ansible_cmd.get_command()))
        # res = ansible_cmd.execute()
        res = ansible_cmd.execute_test()
        self._logger.debug("The provisioning result of Ansible: {}".format(res))

        tend = datetime.datetime.now()
        elasped_time = (tend - tstart).total_seconds()

        result_msg = "Installation Complete. Box: {}, Software: {}, Elasped Time: {}".format(box_desc.name,
                                                                                             target_software.name,
                                                                                             elasped_time)
        return result_msg

    def _generate_ansible_inventory(self, _box_desc):
        # This function generates a temporary ansible inventory file from box_desc
        # Return the full path of the generated inventory file.
        _inventory = {}

        _box = {}

        for net in _box_desc.network:
            if net.plane.lower() == "management":
                _box["ansible_host"] = net.ipaddr
        _box["ansible_user"] = _box_desc.account.get("id", "ubuntu")

        _inventory["all"] = {}
        _inventory["all"]["children"] = {}
        _inventory["all"]["children"][_box_desc.name] = _box

        _inven_str = yaml.dump(_inventory)
        self._logger.debug(_inven_str)

        return _inven_str

    def _create_temp_inventory(self, _inven_str, _file_name):
        _file_full_path = os.path.join(os.path.dirname(__file__), _file_name)

        with open(_file_full_path, mode='w', encoding='utf-8') as stream:
            stream.write(_inven_str)

        return _file_full_path

    def _del_temp_inven_file(self, _file_path):
        os.remove(_file_path)

    def _get_func_install_command(self, function_desc, _inven_file_path):
        playbook_file = "{}/{}".format(self.playbook_config["root_dir"], "function")
        for w in function_desc.type.split("."):
            playbook_file = "{}/{}".format(playbook_file, w)
        playbook_file = "{}/{}".format(playbook_file, "compose.yaml")

        ext_vars = dict()
        for k, v in vars(function_desc).items():
            if v:
                ext_vars[k] = v

        if "output_interval" not in ext_vars.keys():
            pass
        if "post_ipaddr" not in ext_vars.keys():
            pass
        if "post_kafka_port" not in ext_vars.keys():
            pass
        if "post_kafka_topic" not in ext_vars.keys():
            pass
        # output_interval
        # post_ipaddr
        # post_kafka_port
        # post_kafka_topic

        cmd = self._create_ansible_command(_inven_file_path, playbook_file, ext_vars)
        return cmd

    def _get_vbox_install_command(self, box_desc, sw_desc, _inven_file_path):
        playbook_file = "{}/{}/{}".format(self.playbook_config["root_dir"],
                                          sw_desc.name,
                                          self.playbook_config[sw_desc.name]["install"])

        ext_vars = dict()
        ext_vars["tenant"] = box_desc.tenant
        ext_vars["vbox_name"] = box_desc.name
        for k, v in sw_desc.option.items():
            ext_vars[k] = v

        cmd = self._create_ansible_command(_inven_file_path, playbook_file, ext_vars)
        return cmd

    def _get_pbox_install_command(self, box_desc, target_software, _inven_file_path):
        playbook_filepath = "{}/{}".format(self.playbook_config["root_dir"], target_software.name)

        software_type = target_software.option.get("type", None)
        if software_type:
            playbook_filepath = "{}/{}/{}".format(playbook_filepath,
                                                target_software.option["type"],
                                                self.playbook_config[target_software.name][software_type]["install"])
        else:
            playbook_filepath = "{}/{}".format(playbook_filepath,
                                            self.playbook_config[target_software.name][software_type]["install"])

        ext_vars = target_software.option

        cmd = self._create_ansible_command(_inven_file_path, playbook_filepath, None)

        return cmd

    def _create_ansible_command(self, inventory, playbook, extra_vars=None):
        cmd = self.AnsibleCommand()
        cmd.add_inventory(inventory)
        cmd.add_playbook(playbook)

        for k, v in extra_vars.items():
            cmd.add_extra_vars(k, v)

        return cmd

    def uninstall(self, box_desc: Box, target_software: Software or Function):
        tstart = datetime.datetime.now()

        ansible_cmd = None

        _inven_str = self._generate_ansible_inventory(box_desc)
        _inven_filepath = self._create_temp_inventory(_inven_str, "{}.yaml".format(box_desc.name))

        if isinstance(target_software, Software):
            if box_desc.type == "virtual.box":
                if box_desc.where == "post":
                    ansible_cmd = self._get_vbox_uninstall_command(box_desc, target_software)
            elif box_desc.type == "physical.box":
                ansible_cmd = self._get_pbox_uninstall_command(box_desc, target_software)

        elif isinstance(target_software, Function):
            ansible_cmd = self._get_func_uninstall_command(box_desc, target_software, _inven_filepath)

        else:
            return

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

    def _get_func_uninstall_command(self, function_desc, _inven_file_path):
        playbook_file = "{}/{}".format(self.playbook_config["root_dir"], "function")
        for w in function_desc.type.split("."):
            playbook_file = "{}/{}".format(playbook_file, w)
        playbook_file = "{}/{}".format(playbook_file, "release.yaml")

        ext_vars = dict()
        ext_vars["name"] = function_desc.name
        ext_vars["where"] = function_desc.where.split(".")
        ext_vars["tenant"] = function_desc.tenant
        ext_vars["type"] = function_desc.type.split(".")
        ext_vars["option"] = function_desc.option

        cmd = self._create_ansible_command(_inven_file_path, playbook_file, ext_vars)
        return cmd

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

        def execute_test(self):
            cmd = self.get_command()
            return cmd

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
                raise ValueError

            return cmd
