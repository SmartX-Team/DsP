import json
import logging
import urllib3
import ipaddress
from pylxd import Client
from pylxd import exceptions as LXDExceptions
from dsp.inventory import inventory_exceptions


class LXDInterface(object):
    def __init__(self):
        self._logger = None

    def initialize(self):
        self._logger = logging.getLogger(self.__class__.__name__)

    def _get_lxd_client(self, host_ip, lxd_password, cert):
        # Self signed certificates can't be used for accessing remote LXD server.
        # In this reason, I disable verification process.
        # But if you have a certificate signed by valid CA, then pass the certificates when calling initialize method.
        host_url = "https://{}:8443".format(host_ip)
        try:
            if cert is not None:
                lxd_client = Client(endpoint=host_url, cert=cert)
            else:
                urllib3.disable_warnings()
                lxd_client = Client(endpoint=host_url, verify=False)

            if lxd_client.trusted is False or lxd_password is not None:
                lxd_client.authenticate(lxd_password)

        except LXDExceptions.ClientConnectionFailed:
            raise inventory_exceptions.InstallerFailException(
                self.__class__.__name__,
                "Fail to connect host: host URL {}".format(host_url))

        except LXDExceptions.LXDAPIException as exc:
            raise inventory_exceptions.InstallerFailException(
                self.__class__.__name__,
                "Fail to authenticate with the given password: host URL {}".format(host_url))

        return lxd_client

    def check_host(self, host_ip, lxd_password):
        lxd_client = self._get_lxd_client(host_ip, lxd_password, None)
        if lxd_client.trusted is True:
            return True
        else:
            return False

    def list_boxes(self, host_ip):
        lxd_client = self._get_lxd_client(host_ip, None, None)
        lxd_boxes = lxd_client.containers.all()
        # formatting to LXD Box format
        return lxd_boxes

    def list_box(self, host_ip, box_name):
        lxd_boxes = self.list_boxes(host_ip)
        for lxd_box in lxd_boxes:
            if lxd_box.name == box_name:
                return lxd_box
        raise inventory_exceptions.InstallerException("Cannot find the LXD box: box {}".format(box_name))

    def create_box(self, host_ip, box_name, image_name):
        lxd_client = self._get_lxd_client(host_ip, None, None)

        config = {'name': box_name, 'source': {'type': 'image', 'alias': image_name}}
        cbox = lxd_client.containers.create(config, wait=True)
        cbox.start()

    def delete_box(self, host_ip, box_name):
        lxd_client = self._get_lxd_client(host_ip, None, None)

        cbox = lxd_client.containers.get(box_name)
        cbox.freeze()
        cbox.delete()

    def list_networks(self, host_ip):
        lxd_client = self._get_lxd_client(host_ip, None, None)
        networks = lxd_client.networks.all()

        managed_networks = list()
        for network in networks:
            if network.managed is True:
                lxd_network = LXDNetwork(network.name, network.type,
                                         network.config.get("ipv4.address"), network.config.get("ipv4.nat"),
                                         network.config.get("ipv6.address"), network.config.get("ipv6.nat"))
                managed_networks.append(lxd_network)

        return managed_networks

    def list_network(self, host_ip, bridge_name):
        networks = self.list_networks(host_ip)
        for network in networks:
            if network.name == bridge_name:
                return network
        raise inventory_exceptions.InstallerException("Cannot find the network: Network {}".format(bridge_name))

    def create_network(self, host_ip, network_name, network_cidr):
        # Current Pylxd (ver 2.2.1) doesn't support create network
        # So we directly use http client to create network.
        lxd_client = self._get_lxd_client(host_ip, None, None)
        httpclient = urllib3.HTTPSConnectionPool(host_ip,  port=8443,
                                                 cert_file=lxd_client.DEFAULT_CERTS[0],
                                                 key_file=lxd_client.DEFAULT_CERTS[1],
                                                 assert_hostname=False)
        request_body = dict()
        request_body["name"] = network_name
        request_body["description"] = "{} managed by DsP".format(network_name)

        request_body_config = dict()
        ip_interface_intstance = ipaddress.ip_interface(network_cidr)

        ip_address_instance = ip_interface_intstance.ip
        if ip_address_instance == ip_interface_intstance.network.network_address:
            ip_address_instance = ip_address_instance + 1

        network_mask = ip_interface_intstance.compressed.split("/")[-1]
        ip_with_mask = "{}/{}".format(ip_address_instance.__str__(), network_mask)

        if isinstance(ip_interface_intstance, ipaddress.IPv4Interface):
            request_body_config["ipv4.address"] = ip_with_mask
            request_body_config["ipv4.nat"] = "true"
            request_body_config["ipv6.address"] = "none"
            request_body_config["ipv6.nat"] = "false"

        elif isinstance(ip_interface_intstance, ipaddress.IPv6Interface):
            request_body_config["ipv4.address"] = "none"
            request_body_config["ipv4.nat"] = "false"
            request_body_config["ipv6.address"] = ip_with_mask
            request_body_config["ipv6.nat"] = "true"

        else:
            pass

        request_body["config"] = request_body_config
        request_body_json = json.dumps(request_body)

        response = httpclient.request('POST', '/1.0/networks',
                                      headers={'Content-Type': 'application/json'},
                                      body=request_body_json)
        #return response

    def delete_network(self, host_ip, network_name):
        # Current Pylxd (ver 2.2.1) doesn't support create network
        # So we directly use http client to create network.
        lxd_client = self._get_lxd_client(host_ip, None, None)
        httpclient = urllib3.HTTPSConnectionPool(host_ip,  port=8443,
                                                 cert_file=lxd_client.DEFAULT_CERTS[0],
                                                 key_file=lxd_client.DEFAULT_CERTS[1],
                                                 assert_hostname=False)

        response = httpclient.request('DELETE', '/1.0/networks/{}'.format(network_name))


class LXDNetwork(object):
    def __init__(self, name, type, ipv4_addr, ipv4_nat, ipv6_addr, ipv6_nat):
        self.name = name
        self.type = type
        self.ipv4_addr = ipv4_addr
        self.ipv4_nat = ipv4_nat
        self.ipv6_addr = ipv6_addr
        self.ipv6_nat = ipv6_nat

if __name__ == "__main__":
    ipaddr = '192.168.124.31'
    pw = "ubuntu"

    lxdif = LXDInterface()
    if lxdif.check_host(ipaddr, pw) is False:
        print "Host is not accessible: host IP {}, LXD PW {}".format(ipaddr, pw)

    lxdif.list_boxes(ipaddr)

    bridge_name = "lxdbr2"
    network_cidr = "192.168.33.0/24"
    #lxdif.create_network(ipaddr, bridge_name, unicode(network_cidr))
    #lxdif.delete_network(ipaddr, bridge_name)

