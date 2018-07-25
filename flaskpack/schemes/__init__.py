import re

from flask_marshmallow import Marshmallow
from marshmallow import MarshalResult

ma = Marshmallow()

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def convert_json(d, convert):
    new_d = {}
    if isinstance(d, list):
        return [convert_json(t, convert) for t in d]
    else:
        for k, v in d.items():
            if isinstance(v, dict):
                new_d[convert(k)] = convert_json(v, convert)
            else:
                new_d[convert(k)] = v
    return new_d


class WeSchema(ma.Schema):
    def dump_camel(self, obj, many=None, update_fields=True, **kwargs):
        print(obj)
        t = ma.Schema.dump(self, obj, many=many, update_fields=update_fields,
                           **kwargs)
        return MarshalResult(convert_json(t.data, underscore_to_camel),
                             t.errors)