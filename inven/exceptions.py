class NotExistRequiredParameterException(Exception):
    def __init__(self, tool, missing_param, message, args):
        super(NotExistRequiredParameterException, self).__init__(message, args)


class InstallerNotWorkingException(Exception):
    def __init__(self, tool, message, args):
        super(InstallerNotWorkingException, self).__init__(message, args)


class FailInstallationException(Exception):
    def __init__(self, tool, message, args):
        super(FailInstallationException, self).__init__(message, args)