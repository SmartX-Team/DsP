class StoreManagerException(Exception):
    def __init__(self, msg, args):
        super(StoreManagerException, self).__init__(msg, args)


class TemplateInterpreterException(Exception):
    def __init__(self, msg, args):
        super(StoreManagerException, self).__init__(msg, args)


class ParameterNotFoundException(TemplateInterpreterException):
    def __init__(self, filename, findkey, findvalue, args):
        if findvalue is not None:
            errmsg = "In the file {}, cannot find element with key {}, value {}".format(filename, findkey, findvalue)
        else:
            errmsg = "In the file {}, cannot find element with key {}".format(filename, findkey)
        super(ParameterNotFoundException, self).__init__(errmsg, args)


class NotImplementedException(Exception):
    def __init__(self, classname, methodname, args):
        # TODO formatting Error Message
        errmsg = "Class {} Method {} is not implemented yet".format(classname, methodname)
        super(NotImplementedException, self).__init__(errmsg, args)
