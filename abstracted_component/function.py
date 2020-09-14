import json
from typing import Dict


class Function:
    def __init__(self):
        self.name: str or None = None
        self.where: str or None = None  # cluster.box
        self.tenant: str or None = None
        self.type: str or None = None
        self.installer: str or None = None
        self.option: dict or None = None

    @classmethod
    def json_decode(cls, o):
        if "__Function__" in o:
            func_inst = Function()
            func_inst.__dict__.update(o["__Function__"])
            return func_inst
        return o


class FunctionJSONEncoder(json.JSONEncoder):
    def default(self, o: Function) -> Dict[str, dict]:
        if isinstance(o, Function):
            res = dict()
            res["name"] = o.name
            res["where"] = o.where
            res["tenant"] = o.tenant
            res["type"] = o.type
            res["installer"] = o.installer
            if o.option:
                res["option"] = o.option

            return {"__Function__": res}
