

#
# Exception Classes for Installer
#
class InventoryException(Exception):
    def __init__(self, msg, args):
        super(InventoryException, self).__init__(msg, args)


class NotImplementedException(InventoryException):
    def __init__(self, classname, methodname, args):
        errmsg = "This method is not implemented: Class {}, Method {}".format(classname, methodname)
        super(NotImplementedException, self).__init__(errmsg, args)


#
# Exception Classes for Installer
#
class InstallerException(InventoryException):
    def __init__(self, msg, args):
        super(InstallerException, self).__init__(msg, args)


class InstallerFailException(InstallerException):
    def __init__(self, installer, reason, args):
        errmsg = "Installation is failed: Installer {}, Reason {}".format(installer, reason)
        super(InstallerFailException, self).__init__(errmsg, args)


class InstallerParameterNotExistException(InstallerException):
    def __init__(self, installer, missing_param, args):
        errmsg = "Installer parameter is not exist: Installer {}, Missing Paramter {}".format(installer, missing_param)
        super(InstallerParameterNotExistException, self).__init__(errmsg, args)


class InstallerNotWorkingException(InstallerException):
    def __init__(self, installer, args):
        # TODO formatting Error Message
        errmsg = "Installer is not working: {}".format(installer)
        super(InstallerNotWorkingException, self).__init__(errmsg, args)


#
# Exception Class for Inventory Manager
#
class InventoryManagerException(InventoryException):
    def __init__(self, msg, args):
        super(InventoryManagerException, self).__init__(msg, args)


class InventoryNotFindInstallerException(InventoryManagerException):
    def __init__(self, installer_name, args):
        errmsg = "Inventory Manager cannot find Installer: {}".format(installer_name)
        super(InventoryNotFindInstallerException, self).__init__(errmsg, args)


#
# Exception Class for Provisioning Coordinator
#
class ProvisioningCoordinatorException(InventoryException):
    def __init__(self, msg, args):
        super(ProvisioningCoordinatorException, self).__init__(msg, args)
