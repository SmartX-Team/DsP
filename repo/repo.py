# -*- coding: utf-8 -*-
import os
import yaml
import base64
import cryptography
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging


class SecuredRepoMgr(object):
    """
    Secured Repository Manager
    This class provides secured management of configuration files for
    automated provisioning (e.g. Playground Template, Box Configuration file)
    and DsP-Installer's Operation.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SecuredRepoMgr, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._boxlist = list()
        self._seckey = None
        self._secseed = None

        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)

    def existbox(self, boxname):
        """
        Check the box exists in Secured Repository by comparing Hostname

        :param boxname: Box Hostname (String)
        :return: if box exists return True, not exists return False
        """

        try:
            pt = os.path.abspath(os.getcwd()) + "/repo/box.yaml"
            fp = open(pt, 'r')
            fr = fp.read()
            fp.close()
        except IOError:
            self._logger.error("Can't open Box Configuration File")
            self._logger.error("Please make box.yaml file and define your box's "\
                               "Configuration by referring a guide.")
            exit(-1)

        byl = yaml.load_all(fr)

        for b in byl:
            if b['boxname'] == boxname:
                self._updatebox(b)
                return True
        return False

    def _updatebox(self, boxconf):
        """
        Remove old BoxConf instance from box list and add new one for sync
        btw the list and box.yaml file

        :param boxconf: A box config information from the file (Dict parsed by YAML)
        :return: None
        """

        for b in self._boxlist:
            if b.boxname == boxconf['boxname']:
                self._boxlist.remove(b)

        tbc = _BoxConf()
        tbc.boxname = boxconf['boxname']
        tbc.accid = boxconf['account']
        tbc.nic = boxconf['nic']

        self._boxlist.append(tbc)

    def getniclist(self, boxname):
        """
        Get a list consisting of detail information of NICs in a box

        :param boxname: Hostname of a box
        :return: A NICs list of the box
        """
        for b in self._boxlist:
            if b.boxname == boxname:
                return b.nic

    def getaccid(self, boxname):
        """
        Get Linux Account ID of a box

        :param boxname: Hostname of a box
        :return: Linux Account ID of the box whose the hostname "boxname"
        """
        for b in self._boxlist:
            if b.boxname == boxname:
                return b.accid

    def load_seckey(self, salt):
        self._secseed = salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256,
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        p = raw_input("Input the password for secured repository: ")
        self._seckey = base64.urlsafe_b64encode(kdf.derive(p))

    def enc_file(self, org_file_path, enc_file_path):
        rf = open(org_file_path, 'r')
        l = rf.read(-1)
        rf.close()

        wf = open(enc_file_path, 'w')
        f = Fernet(self._seckey)
        wf.write(f.encrypt(l))
        wf.close()

    def dec_file(self, enc_file_path, dec_file_path):
        rf = open(enc_file_path, 'r')
        l = rf.read(-1)
        rf.close()

        wf = open(dec_file_path, 'w')
        f = Fernet(self._seckey)
        try:
            wf.write(f.decrypt(l))
        except cryptography.fernet.InvalidToken:
            self._logger.error("Password or Salt is not correct.")

        wf.close()


class _BoxConf:
    """
    Box Configuration Element
    This instance is used by Secured Repository Manager class
    to store box specific parameter such as hostname, nic list, and so on.
    """
    def __init__(self):
        self.boxname = ""
        self.nic = list()
        self.accid = ""

if __name__ == "__main__":
    """
    bn = "C1-GJ1"
    sr = SecuredRepoMgr()

    chk = sr.existbox(bn)
    if chk:
        print "Box "+bn+" is exists"
    else:
        print "Box "+bn+" is not exists"
        exit(-1)

    print sr.getaccid(bn)
    print sr.getniclist(bn)
    """
    sr = SecuredRepoMgr()
    ts = os.urandom(16)
    sr.load_seckey(ts)
    sr.enc_file("./pgtmpl.yaml", "./pgtmpl.yaml.sec")
    sr.dec_file("./pgtmpl.yaml.sec", "./pgtmpl.yaml.dec")
