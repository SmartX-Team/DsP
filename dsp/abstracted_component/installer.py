import abc


class Installer(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.name = str
        self.version = str
        self.software = list
        self.setting = dict

    @abc.abstractmethod
    def initialize(self, setting_file):
        pass

    @abc.abstractmethod
    def install(self, playground):
        pass

    @abc.abstractmethod
    def uninstall(self, playground):
        pass

    @abc.abstractmethod
    def update(self, playground):
        pass

    @abc.abstractmethod
    def check_status(self):
        pass

    class InstallerStatus:
        Available = 1
        Fail = 2
        Disabled = 3
