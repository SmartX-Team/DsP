import abc


class Installer(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.name = str
        self.version = str
        self.software = list
        self._setting = dict

    @abc.abstractmethod
    def initialize(self, setting_file):
        pass

    @abc.abstractmethod
    def install(self, box_desc, target_software):
        pass

    @abc.abstractmethod
    def uninstall(self, box_desc, target_software):
        pass

    @abc.abstractmethod
    def update(self, box_desc, target_software):
        pass

    @abc.abstractmethod
    def check_status(self):
        pass

    class InstallerStatus:
        Available = 1
        Fail = 2
        Disabled = 3
