import json
from typing import Dict


class Software(object):
    def __init__(self):
        self.name: str or None = None
        self.version: str or None = None
        self.installer: str or None = None
        self.option: dict or None = None

    @classmethod
    def json_decode(cls, o):
        if "__Software__" in o:
            soft_inst = Software()
            soft_inst.__dict__.update(o["__Software__"])
            return soft_inst
        return o


class SoftwareJSONEncoder(json.JSONEncoder):
    def default(self, o: Software) -> Dict[str, dict]:
        if isinstance(o, Software):
            res = dict()
            res["name"] = o.name
            res["version"] = o.name
            res["installer"] = o.installer

            if o.option:
                res["option"] = o.option

            return {"__Software__": res}
