import unittest
import os
import yaml
from maas import client as maas_client


class MAASUnitTests(unittest.TestCase):

    def test_setting_file_exists(self):
        fp = os.path.join(os.path.dirname(__file__), "setting.yaml")
        with open(fp, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr)
        self.assertIsInstance(fy, dict)

    def test_maas_connectable(self):
        fp = os.path.join(os.path.dirname(__file__), "setting.yaml")
        with open(fp, 'r') as stream:
            fr = stream.read(-1)
            fy = yaml.load(fr)

        _setting = fy["config"]
        maas_ip = _setting['maas_ip']
        maas_port = _setting['maas_port']
        maas_url = "http://{}:{}/MAAS/".format(maas_ip, maas_port)

        apikey = _setting['apikey']
        # Todo Creating MAAS Instance with ID/PW
        _interface = maas_client.connect(maas_url, apikey=apikey)
        self.assertIsNotNone(_interface)


if __name__ == '__main__':
    unittest.main()
