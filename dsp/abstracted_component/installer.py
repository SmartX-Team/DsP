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
    def install(self, template):
        pass

    @abc.abstractmethod
    def uninstall(self, template):
        pass

    @abc.abstractmethod
    def update(self, template):
        pass

    @abc.abstractmethod
    def is_available(self):
        pass

    @abc.abstractmethod
    def validate_template(self, template):
        pass

    @abc.abstractmethod
    def get_setting(self):
        pass
