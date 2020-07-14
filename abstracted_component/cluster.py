from typing import Dict, List
from abstracted_component.box import Box, BoxJSONEncoder
from abstracted_component.function import Function, FunctionJSONEncoder
import json


class Cluster:
    def __init__(self):
        self.name: str or None = None
        self.boxes: List[Box] or None = None
        self.functions: List[Function] or None = None

    @classmethod
    def json_decode(cls, o):
        if "__Cluster__" in o:
            c = Cluster()
            c.__dict__.update(o["__Cluster__"])

            if c.boxes:
                box_insts = list()
                for b in c.boxes:
                    box_inst = json.loads(b, object_hook=Box.json_decode)
                    box_insts.append(box_inst)
                c.boxes = box_insts

            if c.functions:
                func_insts = list()
                for f in c.functions:
                    func_inst = json.loads(f, object_hook=Function.json_decode)
                    func_insts.append(func_inst)
                c.functions = func_insts

            return c

        return o


class ClusterJSONEncoder(json.JSONEncoder):
    def default(self, o: Cluster) -> dict:
        if isinstance(o, Cluster):
            res = dict()
            res["name"] = o.name

            if o.boxes:
                res["boxes"] = list()
                for b in o.boxes:
                    res["boxes"].append(json.dumps(b, cls=BoxJSONEncoder))

            if o.functions:
                res["functions"] = list()
                for f in o.functions:
                    res["functions"].append(json.dumps(f, cls=FunctionJSONEncoder))

            return {"__Cluster__": res}
