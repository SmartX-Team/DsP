

#
# Exception Classes for Installer
#
class InventoryException(Exception):
    def __init__(self, msg):
        super(InventoryException, self).__init__(msg)


#
# Exception Classes for Installer
#
class InstallerException(InventoryException):
    def __init__(self, msg):
        super(InstallerException, self).__init__(msg)


class InstallerFailException(InstallerException):
    def __init__(self, installer, reason):
        errmsg = "Installation is failed: Installer {}, Reason {}".format(installer, reason)
        super(InstallerFailException, self).__init__(errmsg)


class InstallerParameterNotExistException(InstallerException):
    def __init__(self, installer, missing_param):
        errmsg = "Installer parameter is not exist: Installer {}, Missing Paramter {}".format(installer, missing_param)
        super(InstallerParameterNotExistException, self).__init__(errmsg)


class InstallerNotWorkingException(InstallerException):
    def __init__(self, installer):
        errmsg = "Installer is not working: {}".format(installer)
        super(InstallerNotWorkingException, self).__init__(errmsg)


class InstallerDisabledException(InstallerException):
    def __init__(self, installer):
        errmsg = "Installer is disabled: {}".format(installer)
        super(InstallerDisabledException, self).__init__(errmsg)


#
# Exception Class for Inventory Manager
#
class InventoryManagerException(InventoryException):
    def __init__(self, msg):
        super(InventoryManagerException, self).__init__(msg)


class InventoryManagerNoInstallerException(InventoryManagerException):
    def __init__(self, installer_name):
        errmsg = "Inventory Manager cannot find Installer: {}".format(installer_name)
        super(InventoryManagerNoInstallerException, self).__init__(errmsg)


class InventoryManagerNoInstallerSettingException(InventoryManagerException):
    def __init__(self, directory_path, setting_file):
        errmsg = "Inventory Manager cannot find Installer's setting file: Directory {}, Setting file {}"\
            .format(directory_path, setting_file)
        super(InventoryManagerNoInstallerSettingException, self).__init__(errmsg)


#
# Exception Class for Provisioning Coordinator
#
class ProvisioningCoordinatorException(InventoryException):
    def __init__(self, msg):
        super(ProvisioningCoordinatorException, self).__init__(msg)
