class InventoryException(Exception):
    def __init__(self, msg, args):
        super(InventoryException, self).__init__(msg, args)


class NotExistRequiredParameterException(InventoryException):
    def __init__(self, tool, missing_param, message, args):
        # TODO formatting Error Message
        errmsg = message
        super(NotExistRequiredParameterException, self).__init__(errmsg, args)


class InstallerNotWorkingException(InventoryException):
    def __init__(self, tool, message, args):
        # TODO formatting Error Message
        errmsg = message
        super(InstallerNotWorkingException, self).__init__(errmsg, args)


class FailInstallationException(InventoryException):
    def __init__(self, tool, message, args):
        # TODO formatting Error Message
        errmsg = message
        super(FailInstallationException, self).__init__(errmsg, args)


class NotImplementedException(InventoryException):
    def __init__(self, classname, methodname, args):
        # TODO formatting Error Message
        errmsg = classname
        super(InstallerNotWorkingException, self).__init__(errmsg, args)
