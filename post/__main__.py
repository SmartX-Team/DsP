import json
import logging

from flask import Flask, request, make_response, jsonify
from post.dsp_post import DsPPost
from abstracted_component.cluster import Cluster

post = DsPPost()
app = Flask(__name__)


@app.route('/topology', methods=['PUT'])
def reload_cluster_topology():
    logging.debug("Received Data: {}".format(request.data))
    cluster_topology = json.loads(request.data)
    post.reload_cluster(cluster_topology)
    resp = make_response("Received", 200)
    return resp


@app.route('/cluster', methods=['POST'])
def compose_cluster():
    logging.debug("Received Data: {}".format(request.data))
    cluster = json.loads(request.data, object_hook=Cluster.json_decode)
    post.compose(cluster)
    resp = make_response("Received", 200)
    return resp


@app.route('/cluster', methods=["PUT"])
def update_cluster():
    cluster = json.loads(request.data, object_hook=Cluster.json_decode)
    post.update_function(cluster)
    resp = make_response("Received", 200)
    return resp


@app.route('/cluster', methods=['DELETE'])
def release_cluster():
    cluster = json.loads(request.data, object_hook=Cluster.json_decode)
    post.release(cluster)
    resp = make_response("Received", 200)
    return resp


@app.route('/installer', methods=["GET"])
def get_installers():
    installers = post.get_installers()
    inst_names = list()

    for installer in installers:
        inst_names.append(installer.name)

    resp = make_response(jsonify({"available_installers": inst_names}), 200)

    return resp


@app.route('/installer/<string:name>', methods=['GET'])
def get_installer(name):
    installer = post.get_installer(name)

    if installer:
        resp = make_response("Exists", 200)
    else:
        resp = make_response("Not Exists", 400)

    return resp


@app.errorhandler(404)
def no_page(error):
    return "Not found the URL", 404


def main():
    logging.basicConfig(format='%(asctime)s-%(levelname)s-%(filename)s:%(lineno)d-%(funcName)s()-%(message)s')
    app.run(host="127.0.0.1", port="8080")
