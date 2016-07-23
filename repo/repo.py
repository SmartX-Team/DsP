# -*- coding: utf-8 -*-
import os.path
import yaml


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
        self._box = list()

    def existbox(self, boxname):
        """
        Check the box exists in Secured Repository by comparing Hostname

        :param boxname: Box Hostname (String)
        :return: if box exists return True, not exists return False
        """

        try:
            pt = os.curdir+'/box.yaml'
            print "pt is "+pt
            fp = open(pt, 'r')
            fr = fp.read()
        except IOError:
            print "Can't open Box Configuration File"
            print "Please make box.yaml file and define your box's"
            print "Configuration by referring a guide."
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

        for b in self._box:
            if b.boxname == boxconf['boxname']:
                self._box.remove(b)

        tbc = _BoxConf()
        tbc.boxname = boxconf['boxname']
        tbc.accid = boxconf['account']
        tbc.nic = boxconf['nic']

        self._box.append(tbc)

    def getniclist(self, boxname):
        """
        Get a list consisting of detail information of NICs in a box
        :param boxname: Hostname of a box
        :return: A NICs list of the box
        """
        for b in self._box:
            if b.boxname == boxname:
                return b.nic

    def getaccid(self, boxname):
        """
        Get Linux Account ID of a box
        :param boxname: Hostname of a box
        :return: Linux Account ID of the box whose the hostname "boxname"
        """
        for b in self._box:
            if b.boxname == boxname:
                return b.accid

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
