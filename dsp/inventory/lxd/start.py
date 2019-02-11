from dsp.abstracted_component.installer import Installer


class LXDInstaller(Installer):
    def __init__(self):
        super(LXDInstaller, self).__init__()
        self.name = "lxd"
        self.version = None
        self.software = list
        self._setting = dict

    def initialize(self, setting_file):
        pass

    def install(self, box_desc):
        pass

    def uninstall(self, box_desc):
        pass

    def update(self, box_desc):
        pass

    def check_status(self):
        pass


if __name__ == "__main__":
    pass