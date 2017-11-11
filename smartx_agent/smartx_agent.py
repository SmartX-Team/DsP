import os
import logging
import json
import platform
import distro
import netifaces

class SmartX_Agent:
    def __init__(self):
        self._logger = None
        self.__init_log()
        self._agent_cfg = None
        self._center = None
        self._collected_data = dict()

    def __init_log(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s')
        sh = logging.StreamHandler()
        sh.setFormatter(fm)
        self.logger.addHandler(sh)

    def start(self):
        self.prepare()
        self.check_conn()
        self.collect_all()
        self.report()

    def prepare(self):
        # Load setting file
        try:
            file_path = os.path.join(os.getcwd(), "agent.yaml")
            self._agent_cfg = self._get_json_obj_from(file_path)
        except json.JSONDecodeError as exc:
            print(exc.args)
            exit(1)
        except FileNotFoundError as exc:
            print(exc.args)

    def _get_json_obj_from(self, path):
        with open(path, "r") as stream:
            json.loads(stream)

    def check_conn(self):
        # Check connectivity to the center (Ping, and ??)
        pass

    def collect_all(self):
        self._collected_data["OS"] = self._collect_os_info()
        self._collected_data["HW"] = self._collect_hw_info()
        self._collected_data["Networking"] = self._collect_networking_info()
        self._collected_data["Package"] = self._collect_installed_packages()
        self._collected_data["Process"] = self._collect_working_process()

    def _collect_os_info(self):
        os_info = dict()
        os_info["machine"] = platform.machine()
        os_info["node"] = platform.node()
        os_info["platform"] = platform.platform()
        os_info["processor"] = platform.processor()
        os_info["release"] = platform.release()
        os_info["system"] = platform.system()
        os_info["version"] = platform.version()
        os_info["uname"] = platform.uname()
        os_info["distro"] = distro._distro
        return os_info

    def _collect_hw_info(self):
        pass

    def _collect_networking_info(self):
        net_info = dict()
        # Collect belows
        # 1. NIC lists
        # 2. IP address of each NIC
        # 3. MAC address of each NIC
        # 4. Networking Namespaces?
        net_info["interface"] = netifaces.interfaces()
        net_info["address"] = netifaces.ifaddresses()
        net_info["gateway"] = netifaces.gateways()
        return net_info

    def _collect_installed_packages(self):
        pkg_info = dict()
        if platform.system() is "linux":
            pass
        else:
            pass
        # Collect belows
        # 1. Package Names
        # 2. Package Versions
        return pkg_info

    def _get_package_list_with_apt(self):
        pass

    def _get_package_list_with_yum(self):
        pass

    def _collect_working_process(self):
        proc_info = dict()
        # Collect belows
        # 1. Working Process list
        # 2. Working Systemd Services
        return proc_info

    def report(self):
        json.dumps(print(self._collected_data))


if __name__ == "__main__":
    smartx_agent = SmartX_Agent()
    smartx_agent.start()
