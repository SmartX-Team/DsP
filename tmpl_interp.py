# -*- coding: utf-8 -*-

import yaml
import os

from repo import repo
from inven import inven
import infoelems
import logging
from flask import Flask

"""
Required REST APIs for Template Interpreter.


"""


app = Flask(__name__)


@app.route("/template/", methods=['GET'])
def get_template_interpreter():
    return "Template Interpreter is alive :)"


class TemplateInterpreter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TemplateInterpreter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self._boxinfo = list()
        self._srmgr = repo.SecuredRepoMgr()
        self._ivmgr = inven.InventoryManager()

        self._logger = logging.getLogger("TemplateInterpreter")
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fm)
        self._logger.addHandler(ch)

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
                self._logger.warn('%s is not in box.yaml...', box['boxname'])
                continue

            swl = list(box['software'])
            for sw in swl:
                swname = sw.keys()[0]
                tsi = self._make_swinfo(swname=swname, ysw_dict=sw.get(swname))
                if not tsi:
                    self._logger.warn('%s is not in Installer Inventory', swname)
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

        swtype = None
        if ysw_dict.has_key('swtype'):
            swtype = ysw_dict['swtype']

        iswinfo = self._ivmgr.prepare(swname=swname, swtype=swtype)
        iswinfo_kl = iswinfo.params.keys()

        if 'parameter' in ysw_dict.keys():
            yswdict_kl = ysw_dict['parameter'].keys()
            for k in yswdict_kl:
                if k in iswinfo_kl:
                    iswinfo.params[k] = ysw_dict['parameter'][k]
                else:
                    self._logger.warn('Parameter %s not defined in Installer', k)

        return iswinfo

if __name__ == "__main__":
    interp = TemplateInterpreter()
    p = os.path.abspath(os.getcwd()) + "/repo/pgtmpl.yaml"

    bl = interp.interp_tmpl(p)

    print ""
    print "-----------------------"
    for b in bl:
        print b

tmpl_interp = TemplateInterpreter()
tmpl_interp.initialize()
app.run(port="22160")
