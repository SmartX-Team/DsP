class NetworkInterface:
    def __init__(self):
        self.nic = str
        self.plane = str
        self.ipaddr = str
        self.gateway = str
        self.subnet = str
        self.dns = list


class Box:
    def __init__(self):
        self.name = str
        self.where = str
        self.tenant = str
        self.type = str
        self.account = list
        self.network = str
        self.setting = dict
        self.software = list


class Cluster:
    def __init__(self):
        self.boxes = list
