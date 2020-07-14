import json
from typing import Dict


class Function:
    def __init__(self):
        self.name = str
        self.where = str  # cluster.box
        self.tenant = str
        self.type = str
        self.installer = str
        self.option = dict

    @classmethod
    def json_decode(cls, o):
        if "__Function__" in o:
            func_inst = Function()
            func_inst.__dict__.update(o["__Function__"])
            return func_inst
        return o


class FunctionJSONEncoder(json.JSONEncoder):
    def default(self, o: Function) -> Dict[str, dict]:
        res = dict()
        res["name"] = o.name
        res["where"] = o.where
        res["tenant"] = o.tenant
        res["type"] = o.type
        res["installer"] = o.installer
        if o.option:
            res["option"] = o.option

        return {"__Function__": res}
