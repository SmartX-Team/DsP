# -*- coding: utf-8 -*-

import yaml
import os
import unicodedata

from repo import repo
from inven import inven
import infoelems


class TemplateInterpreter:
    def __init__(self):
        self._boxinfo = list()
        self._srmgr = repo.SecuredRepoMgr()
        self._ivmgr = inven.InventoryManager()

    def interp_tmpl(self, tpath):
        """
        Parsing the Playground Template and making an instance containing
        all detailed information for automated provisioning, such as
        targeted box address, installing Software, installers etc. .

        :param tpath: The Playground Template's path
        :return: A list of BoxInfo instances
        """
        fp = open(tpath, 'r')
        t = fp.read()

        for box in yaml.load_all(t):
            tbi = self._make_boxinfo(box)
            if not tbi:
                print box['boxname'] + " is not in box.yaml"
                continue

            sd = dict(box['software'])
            for k in sd.keys():
                tsi = self._make_swinfo(k, dict(sd).get(k))
                if not tsi:
                    print k + " is not in Installer Inventory"
                    continue
                tbi.sw.append(tsi)

            self._boxinfo.append(tbi)

        return self._boxinfo

    def _make_boxinfo(self, ybox_dict):
        """
        This method make a BoxInfo instance and return it to caller.
        To make the instance, it interact with SecuredRepositoryManager instance.

        :param ybox_dict: A dictionary variable parsed from Playground Template
        :return: A BoxInfo instance
        """
        if not self._srmgr.existbox(ybox_dict['boxname']):
            return None

        tmpbinfo = infoelems.BoxInfo()
        tmpbinfo.name = ybox_dict['boxname']
        tmpbinfo.type = ybox_dict['type']
        tmpbinfo.nic = self._srmgr.getniclist(ybox_dict['boxname'])
        tmpbinfo.accid = self._srmgr.getaccid(ybox_dict['boxname'])
        return tmpbinfo

    def _make_swinfo(self, swname, ysw_dict):
        """
        This method checks the existence of a software, make a SwInfo instance and return it to caller.
        To make the SwInfo instance, this method communcates with Installer Inventory instance.
        A SwInfo instance returned from Inventory has all parameter variables, and their default value.
        And parameters from the Template will modify default value of the SwInfo instance.
        If making the SwInfo instance successes, then return the instance. If not, return None.

        :param swname: A software title
        :param ysw_dict: A dictionary containing the "swname" Software's parameters defined in Playground Template
        :return: A SwInfo instance filled with parameters parse\d from Playground Template & Installer Inventory
        """

        if not self._ivmgr.verify(swname):
            return None

        iswinfo = self._ivmgr.prepare(swname, ysw_dict['swtype'])

        iswinfo_kl = iswinfo.params.keys()
        yswdict_kl = ysw_dict.keys()
        yswdict_kl.remove('swtype')

        for k in yswdict_kl:
            if k in iswinfo_kl:
                iswinfo.params[k] = ysw_dict[k]
            else:
                print "Parameter " + k + " not defined in Installer"

        return iswinfo

if __name__ == "__main__":
    interp = TemplateInterpreter()
    # p = "/home/jun/DsP-Installer/repo/pgtmpl.yaml"
    p = os.path.abspath(os.getcwd()) + "/repo/pgtmpl.yaml"

    bl = interp.interp_tmpl(p)

    print ""
    print "-----------------------"
    for b in bl:
        print b
