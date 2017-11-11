import os
from flask import Flask
import yaml
import logging

app = Flask(__name__)

"""
When initialize, Inventory Manager should detect all supervisors,
and set IDs to each.

Required REST APIs for Inventory Manager
    - GET manager's status (/inventory/)
    - GET supervisor's parameters
      (/inventory/supervisors/<string:supervisor_id>/parameter)
    - GET supervisor's config
      (/inventory/supervisors/<string:supervisor_id>/config)
    - GET supervisor list (/inventory/supervisors/)

APIs will be added
    POST add supervisor
    DELETE supervisor
"""


@app.route("/inventory/", methods=['GET'])
def get_manager_status():
    resp = dict()
    resp['message'] = "Inventory Manager is working!!"
    return yaml.dump(resp)


@app.route("/inventory/supervisor/priority/", methods=['GET'])
def get_software_priority():
    return yaml.dump(inven_manager.software_priority)


@app.route("/inventory/supervisor/", methods=['GET'])
def get_supervisor_list():
    inven_manager.update_supervisors()
    return yaml.dump(inven_manager.supervisors_list)
    # return yaml.dump(inven_manager.get_supervisors())


@app.route("/inventory/supervisor<string:supervisor_id>", methods=['GET'])
def get_supervisor_detail(supervisor_id):
    for sv in inven_manager.supervisor_list:
        if sv['supervisor_id'] == supervisor_id:
            return yaml.dump(sv)
    return "Can not found Supervisor whose ID "+supervisor_id + \
           ". Error Code: 404"


@app.route("/inventory/supervisor/<string:supervisor_id>/setting/",
           methods=['GET'])
def get_supervisor_config(supervisor_id):
    for sv in inven_manager.supervisors_list:
        print sv
        if sv['supervisor_id'] == supervisor_id:
            sv.pop('parameter')
            return yaml.dump(sv)
    return "Can not found Supervisor whose ID "+supervisor_id + \
           ". Error Code: 404"


@app.route("/inventory/supervisor/<string:supervisor_id>/parameter",
           methods=['GET'])
def get_supervisor_parameter(supervisor_id):
    for sv in inven_manager.supervisors_list:
        print sv
        if sv['supervisor_id'] == supervisor_id:
            return yaml.dump(sv['parameter'])
    return "Can't found Supervisor whose ID "+supervisor_id + \
           ". Error Code: 404"


class InventoryManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(InventoryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.supervisors_list = list()
        self.software_priority = dict()

        self._logger = logging.getLogger("InventoryManager")
        self._logger.setLevel(logging.DEBUG)
        fm = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(fm)
        self._logger.addHandler(ch)

    def initialize(self):
        self.update_supervisors()

        p = os.path.abspath(os.getcwd()) + "/setting.yaml.tmpl"
        fp = open(p, mode='r')
        t = fp.read(-1)
        fp.close()
        self.software_priority = yaml.load(t)

    def get_supervisors(self):
        _supervisor_dict = dict()
        for sv in self.supervisors_list:
            _supervisor_dict[sv['name']] = sv['supervisor_id']
        return _supervisor_dict

    def update_supervisors(self):
        _p = os.path.abspath(os.getcwd())
        subdir = [d for d in os.listdir(_p) if
                  os.path.isdir(os.path.join(_p, d))]

        for d in subdir:
            if "setting.yaml.tmpl" in os.listdir(os.path.join(_p, d)):
                self._logger.debug("Load setting.yaml.tmpl in " +
                                   os.path.join(_p, d, "setting.yaml.tmpl"))
                fp = open(os.path.join(_p, d, "setting.yaml.tmpl"), mode='r')
                svcfg = yaml.load(fp.read())
                self._add_supervisor_dict(svcfg, os.path.join(_p, d))

    def _add_supervisor_dict(self, __svcfg, __path):
        _svname = __svcfg['name']

        for sv in self.supervisors_list:
            if sv['name'] == _svname:
                self._logger.info("Install Supervisor " + _svname +
                                  "is already registered")
                return

        if self.supervisors_list:
            lastkey = self.supervisors_list[-1]['supervisor_id']
            k = int(lastkey) + 1
        else:
            k = 1

        __svcfg['supervisor_id'] = str(k)
        __svcfg['path'] = __path
        self._logger.info("Install Supervisor " + _svname +
                          " is added with the key " + str(k))
        self.supervisors_list.append(__svcfg)

    def _sort_dict(self, __dict, __key):
        return sorted(__dict, key=lambda k: k[__key])

inven_manager = InventoryManager()
inven_manager.initialize()
app.run(port="22730")
