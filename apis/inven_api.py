import os
from flask import Flask
import yaml
import inven_api.inven.inven
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

inven_manager = inven_api.inven_api.InventoryManager()
inven_manager.initialize()
app.run(port="22730")
