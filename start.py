# -*- coding: utf-8 -*-
import os

from tmpl_interp import TemplateInterpreter
from prov.prov import ProvisionCoordinator


class DsPInstaller:
    def __init__(self):
        self._tmpl_interp = TemplateInterpreter()
        self._prov_coordi = ProvisionCoordinator()

    def start(self):
        tmpl_path = os.path.join(os.getcwd(), "repo", "pgtmpl.yaml")
        prov_info = self._tmpl_interp.interp_tmpl(tmpl_path)
        self._prov_coordi.prov_playground(prov_info)

if __name__ == '__main__':
    dsp_inst = DsPInstaller()
    dsp_inst.start()
