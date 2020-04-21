import logging
import yaml
from dsp.inventory.inventory_exceptions import *
from dsp.inventory import __all__ as installer_classes


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
        self._logger.info("{} is initialized".format(self.__class__.__name__))

    def _register_installers(self):
        for installer_class in installer_classes:
            installer_instance = installer_class()
            self._registered_installers.append(installer_instance)

    def get_installer(self, installer_name):
        try:
            matched_installer = self._get_installer_from_list(installer_name)
        except InventoryManagerNoInstallerException as exc:
            # ToDo If no installer in the list, need to find sub directories rather than raise an exception.
            raise InventoryManagerException(exc)

        try:
            self._check_installer(matched_installer)
        except InstallerNotWorkingException as exc:
            raise InventoryManagerException(exc)
        except InstallerDisabledException as exc:
            raise InventoryManagerException(exc)
        return matched_installer

    def _get_installer_from_list(self, installer_name):
        for installer_instance in self._registered_installers:
            if installer_instance.name.lower() == installer_name.lower():
                return installer_instance
        raise InventoryManagerNoInstallerException(installer_name)

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
