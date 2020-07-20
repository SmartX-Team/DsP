import logging
import yaml

from abstracted_component.inst_tool_iface import InstallationToolInterface
from typing import List

from post.inventory.inventory_exceptions import *
from post.inventory import __all__ as installer_classes


class InventoryManager(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InventoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._registered_installers: List[InstallationToolInterface] = list()
        self._logger: logging = logging.getLogger(self.__class__.__name__)
        self._register_installers()

    def _register_installers(self):
        for installer_class in installer_classes:
            installer_instance = installer_class()
            self._registered_installers.append(installer_instance)

    def get_installers(self):
        return self._registered_installers

    def get_installer(self, _prefix, _postfix=None):
        if _postfix:
            _fullname = "{}.{}".format(_prefix, _postfix)
        else:
            _fullname = _prefix

        _installer = self._get_installer_from_list(_fullname)
        if _installer:
            return _installer

        for installer_class in installer_classes:
            if installer_class.name_prefix == _prefix:
                _installer = installer_class()
                self._registered_installers.append(_installer)
                return _installer

    def _get_installer_from_list(self, _name):
        for installer_instance in self._registered_installers:
            self._logger.debug("instance name: {} / installer name: {}".format(installer_instance.name, _name))
            if installer_instance.name.lower() == _name.lower():
                return installer_instance
        return None

    def _register_installer(self, _installer_name_prefix, _where):
        if _where:
            _full_installer_name = "{}.{}".format(_installer_name_prefix, _where)
        else:
            _full_installer_name = _installer_name_prefix

        for installer_class in installer_classes:
            self._logger.debug(
                "instance name: {} / installer name: {}".format(installer_class.name_prefix, _full_installer_name))
            if installer_class.name_prefix == _installer_name_prefix:
                _installer_instance = installer_class()
                _installer_instance.name = _full_installer_name
                self._registered_installers.append(_installer_instance)
                self._logger.debug("A new installer was created and registered: {}".format(_installer_instance.name))
                return _installer_instance

        self._logger.debug("Installer {} does not supported".format(_installer_name_prefix))
        return None

    def _check_installer(self, installer_instance):
        installer_status = installer_instance.check_tool_status()
        if installer_status == installer_instance.InstallationToolStatus.Fail:
            raise InstallerNotWorkingException(installer_instance.name)
        elif installer_status == installer_instance.InstallationToolStatus.Disabled:
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
