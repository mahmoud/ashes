from __future__ import unicode_literals

import re
import json

__all__ = ['AshesTest', 'json_rtrip', 'camel2under', 'under2camel']

_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))


class ATMeta(type):
    def __new__(cls, name, bases, attrs):
        ret = super(ATMeta, cls).__new__(cls, name, bases, attrs)
        ret.name = camel2under(name)
        return ret

    @property
    def context(cls):
        try:
            return json.loads(cls.json_context)
        except:
            return None

    @property
    def ast(cls):
        if getattr(cls, 'json_ast', None):
            return json.loads(cls.json_ast)
        return None

    @property
    def opt_ast(cls):
        if getattr(cls, 'json_opt_ast', None):
            return json.loads(cls.json_opt_ast)
        return None

    def __repr__(self):
        return 'AshesTest(%r)' % self.name



class AshesTest(object):
    template = None
    json_ast = None
    json_opt_ast = None
    json_context = None
    rendered = None

    __metaclass__ = ATMeta



def json_rtrip(obj, raise_exc=False):
    try:
        if isinstance(obj, basestring):
            return json.dumps(json.loads(obj))
        return json.loads(json.dumps(obj))
    except:
        if raise_exc:
            raise
        return obj
