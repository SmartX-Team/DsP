from abstracted_component.inst_tool_iface import InstallationToolInterface


class LXDInstallationToolInterface(InstallationToolInterface):
    def __init__(self):
        super(LXDInstallationToolInterface, self).__init__()
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

    def check_tool_status(self):
        pass


if __name__ == "__main__":
    pass