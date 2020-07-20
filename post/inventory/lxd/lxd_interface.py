import json
import logging
import urllib3
import ipaddress
from pylxd import Client
from pylxd import exceptions as LXDExceptions
from post.inventory import inventory_exceptions


class LXDInterface(object):
    def __init__(self):
        self._logger = None
        self.initialize()

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

            if lxd_client.trusted is False:
                if lxd_password is not None:
                    lxd_client.authenticate(lxd_password)
                else:
                    raise inventory_exceptions.InstallerFailException(
                        self.__class__.__name__,
                        "Fail to authenticate with empty password: host URL {}".format(host_url))

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
        try:
            lxd_client = self._get_lxd_client(host_ip, lxd_password, None)
        except inventory_exceptions.InstallerFailException as exc:
            raise inventory_exceptions.InstallerException(exc.message)


    def list_boxes(self, host_ip):
        # ToDo Implement
        lxd_client = self._get_lxd_client(host_ip, None, None)
        lxd_boxes = lxd_client.containers.all()
        # formatting to LXD Box format
        return lxd_boxes

    def list_box(self, host_ip, box_name):
        # ToDo Implement
        lxd_boxes = self.list_boxes(host_ip)
        for lxd_box in lxd_boxes:
            if lxd_box.name == box_name:
                return lxd_box
        raise inventory_exceptions.InstallerException("Cannot find the LXD box: box {}".format(box_name))

    def create_box(self, host_ip, box_name, image_name):
        lxd_client = self._get_lxd_client(host_ip, None, None)

        self._logger.info("Create LXD Box / Host IP address: {}, LXD Box Name: {}, LXD Image: {}"
                          .format(host_ip, box_name, image_name))

        config = {'name': box_name, 'source': {'type': 'image', 'alias': image_name}}
        cbox = lxd_client.containers.create(config, wait=True)

        self._logger.info("Start LXD Box / Host IP address: {}, LXD Box Name: {}, LXD Image: {}"
                          .format(host_ip, box_name, image_name))
        cbox.start()

        self._logger.info("Finish creating LXD Box / Host IP address: {}, LXD Box Name: {}, LXD Image: {}"
                          .format(host_ip, box_name, image_name))

    def remove_box(self, host_ip, box_name):
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
        raise inventory_exceptions.InstallerFailException(self.__class__.__name__,
                                                          "Cannot find the network: Network {}".format(bridge_name))

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
        return response

    def remove_network(self, host_ip, network_name):
        # Current Pylxd (ver 2.2.1) doesn't support create network
        # So we directly use http client to create network.
        lxd_client = self._get_lxd_client(host_ip, None, None)
        httpclient = urllib3.HTTPSConnectionPool(host_ip,  port=8443,
                                                 cert_file=lxd_client.DEFAULT_CERTS[0],
                                                 key_file=lxd_client.DEFAULT_CERTS[1],
                                                 assert_hostname=False)

        response = httpclient.request('DELETE', '/1.0/networks/{}'.format(network_name))

    def update_network(self, host_ip, network_name):
        raise inventory_exceptions.InstallerFailException(
            self.__class__.__name__,
            "This function is not implemented: function {}".format(function.__name__))

    def list_images(self, host_ip):
        lxd_client = self._get_lxd_client(host_ip, None, None)
        lxd_images = lxd_client.images.all()
        return lxd_images

    def list_image(self, host_ip, image_name):
        images = self.list_images(host_ip)

        for img in images:
            if img.update_source.get("alias") == image_name:
                return img

        return None

    def create_image(self, host_ip, image_name):
        lxd_client = self._get_lxd_client(host_ip, None, None)

        ubuntu_repo_url = "https://cloud-images.ubuntu.com/releases/"

        img = self.list_image(host_ip, image_name)
        if img:
            self._logger.debug("LXC Image already exists. Don't copy Image: {}".format(image_name))
            return img

        self._logger.info("Download LXD image / Host IP: {}, Server: {}, Image Name: {}")\
            .format(host_ip, ubuntu_repo_url, image_name)
        create_image = lxd_client.images.create_from_simplestreams(ubuntu_repo_url, image_name)

        self._logger.info("Add Alias to Image / Host IP: {}, Alias: {}, Image Name: {}")\
            .format(host_ip, image_name, image_name)
        create_image.add_alias(image_name, "Image managed by DsP")

        self._logger.info("Finish creating Image / Host IP: {}, Image Name: {}").format(host_ip, image_name)
        return create_image

    def remove_image(self, host_ip, image_name):
        pass

    def list_profiles(self, host_ip):
        pass

    def list_profile(self, host_ip, profile_name):
        pass

    def create_profile(self, host_ip, profile_name):
        pass

    def remove_profile(self, host_ip, profile_name):
        pass


class LXDBox(object):
    def __init__(self, name, profile, image, config, networks):
        self.name = name
        self.profile = profile
        self.image = image
        self.config = config
        self.networks = networks


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
        print("Host is not accessible: host IP {}, LXD PW {}".format(ipaddr, pw))

    box_name = "testbox1"
    image_name = "16.04"
    bridge_name = "lxdbr2"
    network_cidr = "192.168.33.0/24"

    lxdif.create_box(ipaddr, box_name, image_name)
    #lxdif.list_boxes(ipaddr)
    # lxdif.create_image(ipaddr, image_name)

    #lxdif.create_network(ipaddr, bridge_name, unicode(network_cidr))
    #lxdif.delete_network(ipaddr, bridge_name)

