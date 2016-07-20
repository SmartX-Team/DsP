class BoxInfo:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.sw = list()

    def getname(self):
        return self.name

    def gettype(self):
        return self.type

    def getswinfo(self):
        return self.sw


class SwInfo:
    def __init__(self):
        self.name = ""
        self.params = dict()

    def getname(self):
        return self.name

    def getparams(self):
        return self.params