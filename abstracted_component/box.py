import json
from typing import Dict, List, Type
from abstracted_component.software import Software, SoftwareJSONEncoder


class NetworkInterface:
    def __init__(self):
        self.nic: str or None = None
        self.plane: str or None = None
        self.ipaddr: str or None = None
        self.gateway: str or None = None
        self.subnet: str or None = None
        self.dns: list or None = None

    @classmethod
    def json_decode(cls, o):
        if "__NetworkInterface__" in o:
            niface_inst: NetworkInterface = NetworkInterface()
            niface_inst.__dict__.update(o["__NetworkInterface__"])
            return niface_inst
        return o


class NetworkInterfaceJSONEncoder(json.JSONEncoder):
    def default(self, o: NetworkInterface) -> Dict[str, dict]:
        if isinstance(o, NetworkInterface):
            res = dict()
            res["nic"] = o.nic
            res["plane"] = o.plane
            res["ipaddr"] = o.ipaddr
            res["gateway"] = o.gateway
            res["subnet"] = o.subnet

            if o.dns and len(o.dns) > 0:
                res["dns"] = list()

                for d in o.dns:
                    res["dns"].append(d)

            return {"__NetworkInterface__": res}


##############################################################################
##############################################################################
class Box:
    def __init__(self):
        self.name: str or None = None      # box hostname
        self.where: str or None = None     # cluster
        self.tenant: str or None = None    # operator, username
        self.type: str or None = None      # physical, virtual, container
        self.account: list or None = None  # Linux account ID
        self.network: List[NetworkInterface] or None = None
        self.setting: dict or None = None
        self.software: List[Software] or None = None

    @classmethod
    def json_decode(cls, o):
        if "__Box__" in o:
            box_inst: Box = Box()
            box_inst.__dict__.update(o["__Box__"])

            if box_inst.network:
                net_insts = list()
                for n in box_inst.network:
                    net_inst: NetworkInterface = json.loads(n, object_hook=NetworkInterface.json_decode)
                    net_insts.append(net_inst)
                box_inst.network = net_insts

            if box_inst.software:
                soft_insts = list()
                for s in box_inst.software:
                    soft_inst: Software = json.loads(s, object_hook=Software.json_decode)
                    soft_insts.append(soft_inst)
                box_inst.software = soft_insts

            return box_inst
        return o


class BoxJSONEncoder(json.JSONEncoder):

    def default(self, o: Box) -> Dict[str, dict]:
        if isinstance(o, Box):
            res = dict()
            res["name"] = o.name
            res["where"] = o.where
            res["tenant"] = o.tenant
            res["type"] = o.type
            res["account"] = o.account

            if o.network:
                res["network"] = list()
                for n in o.network:
                    res["network"].append(json.dumps(n, cls=NetworkInterfaceJSONEncoder))

            res["setting"] = o.setting

            res["software"] = list()
            if len(o.software) > 0:
                for s in o.software:
                    res["software"].append(json.dumps(s, cls=SoftwareJSONEncoder))

            return {"__Box__": res}
