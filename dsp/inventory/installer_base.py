import abc


class InstallerBase(object):
    __metaclass__ = abc.ABCMeta

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
