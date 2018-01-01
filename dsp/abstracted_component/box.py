class Box:
    def __init__(self):
        self.name = str
        self.type = str
        self.account = list
        self.network = str
        self.setting = dict
        self.software = list

    class NetworkInterface:
        def __init__(self):
            self.name = str
            self.ipaddr = str
            self.gateway = str
            self.subnet = str
            self.dns = str
