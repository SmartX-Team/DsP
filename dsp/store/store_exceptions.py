class StoreManagerException(Exception):
    def __init__(self, msg):
        super(StoreManagerException, self).__init__(msg)


class TemplateInterpreterException(Exception):
    def __init__(self, msg):
        super(TemplateInterpreterException, self).__init__(msg)


class ParameterNotFoundException(TemplateInterpreterException):
    def __init__(self, filename, findkey, findvalue):
        if findvalue is not None:
            errmsg = "Cannot Find Element: file {}, key {}, value {}".format(filename, findkey, findvalue)
        else:
            errmsg = "Cannot Find Element: file {}, key {}".format(filename, findkey)
        super(ParameterNotFoundException, self).__init__(errmsg)


class NotDefinedBoxException(TemplateInterpreterException):
    def __init__(self, box_name):
        errmsg = "In Box file, cannot find a box whose the given name: box {}".format(box_name)
        super(NotDefinedBoxException, self).__init__(errmsg)


class NotImplementedException(Exception):
    def __init__(self, classname, methodname):
        # TODO formatting Error Message
        errmsg = "Class {} Method {} is not implemented yet".format(classname, methodname)
        super(NotImplementedException, self).__init__(errmsg)
