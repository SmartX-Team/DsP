import os
import logging
import yaml
import platform
import distro
import netifaces
import apt
import psutil

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
            self._agent_cfg = self._get_yaml_obj_from(file_path)
        except yaml.YAMLError as exc:
            print(exc.args)
            exit(1)
        except Exception as exc:
            print(exc.args)

    def _get_yaml_obj_from(self, path):
        with open(path, "r") as stream:
            return yaml.load(stream)

    def check_conn(self):
        # Check connectivity to the center (Ping, and ??)
        pass

    def collect_all(self):
        if platform.system() == "Linux":
            self.collect_all_linux()
        else:
            raise TypeError("Currently, this agent only supports Linux Operating Systems!")

    def collect_all_linux(self):
        self._collected_data["OS"] = self.collect_os_info()
        self._collected_data["HW"] = self.collect_hw_info()
        self._collected_data["Networking"] = self.collect_networking_info()
        self._collected_data["Package"] = self.collect_installed_packages()
        self._collected_data["Process"] = self.collect_working_process()

    def collect_os_info(self):
        os_info = dict()
        os_info["type"] = platform.system() # Linux / Windows
        os_info["distro"] = distro.id()
        os_info["version"] = distro.version()
        os_info["codename"] = distro.codename()
        os_info["arch"] = platform.machine() # Architecture
        os_info["kernel_version"] = platform.release() # Kernel version
        return os_info

    def collect_hw_info(self):
        hw_info = dict()
        self._collect_cpu_info(hw_info)
        self._collect_mem_info(hw_info)
        self._collect_disk_info(hw_info)
        return hw_info

    def _collect_cpu_info(self, hw_info):
        hw_info["cpu_phy_count"] = psutil.cpu_count()
        hw_info["cpu_log_count"] = psutil.cpu_count(logical=False)
        hw_info["cpu_used"] = psutil.cpu_percent()

    def _collect_mem_info(self, hw_info):
        mem_info = psutil.virtual_memory()
        hw_info["mem_total"] = mem_info.total
        hw_info["mem_used"] = mem_info.used
        hw_info["mem_free"] = mem_info.available

    def _collect_disk_info(self, hw_info):
        disk_info = psutil.disk_usage('/')
        hw_info["storage_total"] = disk_info.total
        hw_info["storage_used"] = disk_info.used
        hw_info["storage_free"] = disk_info.free

    def collect_networking_info(self):
        net_info = dict()
        net_info["interfaces"] = self._collect_net_interfaces_info()
        return net_info

    def _collect_net_interfaces_info(self):
        ifaces = dict()
        for dev in netifaces.interfaces():
            ifaces[dev] = self._get_dev_addr(dev)
        return ifaces

    def _get_dev_addr(self, dev):
        customized_addr_list = dict()
        org_addr_list = netifaces.ifaddresses(dev)
        customized_addr_list["ipv4"] = self._get_dev_ipv4_addr_from(org_addr_list)
        customized_addr_list["mac"] = self._get_dev_mac_addr_from(org_addr_list)
        return customized_addr_list

    def _get_dev_ipv4_addr_from(self, org_addr_list):
        return org_addr_list[2]

    def _get_dev_mac_addr_from(self, org_addr_list):
        return org_addr_list[17]

    def collect_installed_packages(self):
        if distro.id() in ["linuxmint"]:
            return self._get_package_list_using_apt()
        else:
            raise TypeError("" + distro.id() + " distribution is not supported yet!")

    def _get_package_list_using_apt(self):
        installed_pkgs_info = dict()
        all_apt_pkgs = apt.Cache()
        for pkg in all_apt_pkgs:
            if pkg.installed:
                installed_pkgs_info[pkg.name] = {"version": pkg.installed.version}
        return installed_pkgs_info

    def _get_package_list_with_yum(self):
        pass

    def collect_working_process(self):
        proc_info = dict()
        for proc in psutil.process_iter():
            proc_info[proc.pid] = {"name": proc.name()}
        return proc_info

    def report(self):
        print self._collected_data
        try:
            print yaml.safe_dump(self._collected_data, default_flow_style=False)
        except yaml.YAMLError as exc:
            print(exc.args)


if __name__ == "__main__":
    smartx_agent = SmartX_Agent()
    smartx_agent.start()
