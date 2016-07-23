# -*- coding: utf-8 -*-


class BoxInfo:
    def __init__(self):
        self.name = ""
        self.type = ""
        self.sw = list()
        self.nic = list()


class SwInfo:
    def __init__(self):
        self.name = ""
        self.params = dict()