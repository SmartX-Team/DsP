class StoreException(Exception):
    def __init__(self, msg, args):
        super(StoreException, self).__init__(msg, args)


class ElementNotFoundException(StoreException):
    def __init__(self, filename, findkey, findvalue, args):
        if findvalue is not None:
            errmsg = "In the file {}, cannot find element with key {}, value {}".format(filename, findkey, findvalue)
        else:
            errmsg = "In the file {}, cannot find element with key {}".format(filename, findkey)
        super(ElementNotFoundException, self).__init__(errmsg, args)


class NotImplementedException(StoreException):
    def __init__(self, classname, methodname, args):
        # TODO formatting Error Message
        errmsg = "Class {} Method {} is not implemented yet".format(classname, methodname)
        super(StoreException, self).__init__(errmsg, args)
