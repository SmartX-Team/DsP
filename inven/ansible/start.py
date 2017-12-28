from ..installer_base import InstallerBase


class AnsibleInstaller(InstallerBase):
    def initialize(self, setting_file):
        pass

    def install(self, template):
        pass

    def uninstall(self, template):
        pass

    def update(self, template):
        pass

    def is_available(self):
        pass

    def validate_template(self, template):
        pass

    def get_setting(self):
        pass