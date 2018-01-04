import sys
import os
import logging
import yaml
import importlib
from inventory_exceptions import *


class InventoryManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InventoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._registered_installers = list()
        self._logger = None

        self._initialize()

    def _initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._register_installers()

    def _register_installers(self):
        # Traverse each sub-directory
        #   load setting.yaml
        #   create installer
        current_path = os.path.abspath(os.getcwd())
        subdirs = self._get_sub_directories(current_path)
        for subdir in subdirs:
            subdir_path = os.path.join(current_path, subdir)
            try:
                installer_instance = self._create_installer_from_subdir(subdir_path)
                self._registered_installers.append(installer_instance)
            except InventoryManagerNoInstallerException as exc:
                self._logger.warn(exc.message)
            except InventoryManagerNoInstallerSettingException as exc:
                self._logger.warn(exc.message)

    def _create_installer_from_subdir(self, subdir_path):
        if "setting.yaml" in os.listdir(subdir_path):
            installer_setting = self._read_yaml_file(os.path.join(subdir_path, "setting.yaml"))
            executable_file = installer_setting.get("executable")
            installer_name = installer_setting.get("name")

            sys.path.insert(0, subdir_path)
            try:
                executable_module = importlib.import_module(executable_file.split(".")[0])
                target_class = getattr(executable_module, installer_name)
                installer_instance = target_class()
                installer_instance.initialize(installer_setting)
            except AttributeError as exc:
                raise InventoryManagerException(exc.message)
            finally:
                sys.path.remove(subdir_path)

            return installer_instance
        else:
            raise InventoryManagerNoInstallerSettingException(subdir_path, "setting.yaml")

    def _get_sub_directories(self, current_path):
        return [d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))]

    def get_installer(self, installer_name):
        try:
            matched_installer = self._get_installer_from_list(installer_name)
        except InventoryManagerNoInstallerException as exc:
            # ToDo If no installer in the list, need to find sub directories rather than raise an exception.
            raise InventoryManagerException(exc.message)

        try:
            self._check_installer(matched_installer)
        except InstallerNotWorkingException as exc:
            raise InventoryManagerException(exc.message)
        except InstallerDisabledException as exc:
            raise InventoryManagerException(exc.message)
        return matched_installer

    def _get_installer_from_list(self, installer_name):
        for installer_instance in self._registered_installers:
            if installer_instance.name == installer_name:
                return installer_instance
        raise InventoryManagerNoInstallerException(installer_name)

    def _check_installer(self, installer_instance):
        installer_status = installer_instance.check_status()
        if installer_status == installer_instance.InstallerStatus.Fail:
            raise InstallerNotWorkingException(installer_instance.name)
        elif installer_status == installer_instance.InstallerStatus.Disabled:
            raise InstallerDisabledException(installer_instance.name)

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
                    errmsg = "YAML Format Error: %s (Position: line %s, column %s)" \
                             % (_file, mark.line + 1, mark.column + 1)
                    raise ProvisioningCoordinatorException(errmsg)


if __name__ == "__main__":
    inven_manager = InventoryManager()
    inven_manager.get_installer("MAASInstaller")
