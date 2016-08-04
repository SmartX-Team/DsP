# -*- coding: utf-8 -*-


class BoxInfo:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.accid = ""
        self.accpw = ""
        self.sw = list()
        self.nic = list()


class SwInfo:
    def __init__(self):
        self.name = ""
        self.path = ""
        self.params = dict()
        self.type = ""
