class BoxInfo:
    def __init__(self):
        self._name = ""
        self._type = ""
        self._sw = list()

    def getname(self):
        return self._name

    def setname(self, name):
        self._name = name

    def gettype(self):
        return self._type

    def settype(self, type):
        self._type = type

    def getswinfo(self):
        return self._sw

    def setswinfo(self, swinfo):
        self._sw.append(swinfo)

class SwInfo:
    def __init__(self):
        self._name = ""
        self._params = dict()

    def getname(self):
        return self._name

    def getparams(self):
        return self._params

    def setparam(self, k, v):
        self._params[k] = v