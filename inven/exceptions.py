class NotExistRequiredParameterException(Exception):
    def __init__(self, tool, missing_param, message, args):
        super(NotExistRequiredParameterException, self).__init__(message, args)
