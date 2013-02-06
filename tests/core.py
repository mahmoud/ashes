from __future__ import unicode_literals

import re
import json
from collections import OrderedDict, namedtuple

__all__ = ['AshesTest', 'json_rtrip', 'camel2under', 'under2camel']

_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))


def json_rtrip(obj, raise_exc=False):
    try:
        if isinstance(obj, basestring):
            return json.dumps(json.loads(obj))
        return json.loads(json.dumps(obj))
    except:
        if raise_exc:
            raise
        return obj


class ATMeta(type):
    def __new__(cls, name, bases, attrs):
        ret = super(ATMeta, cls).__new__(cls, name, bases, attrs)
        ret.name = camel2under(name)
        return ret

    @property
    def context(cls):
        try:
            return cls.__dict__['context']
        except KeyError:
            pass
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


###########################
# Test result stuff follows
###########################


class SkipTest(Exception):
    pass


SYMBOLS = {'passed': '.', 'failed': 'X', 'skipped': '_', 'error': 'E'}

AshesTestBase = ATMeta(str('AshesTestBase'), (object,), {})


class AshesTest(AshesTestBase):
    template = None
    json_ast = None
    json_opt_ast = None
    json_context = None
    rendered = None

    # __metaclass__ = ATMeta

    @classmethod
    def get_test_result(cls, env, lazy=False, raise_exc=False):
        return AshesTestResult(cls, env, lazy, raise_exc)


DTR = namedtuple('DiffableTestResult', 'op_name result ref_result test_result')
DTO = namedtuple('DiffableTestOp', 'op_name get_test_result get_ref_result')

OPS = [DTO('tokenize', lambda tmpl, tc: tmpl._get_tokens(), None),
       DTO('parse',
           lambda tmpl, tc: json_rtrip(tmpl._get_ast(raw=True)),
           lambda tc: tc.ast),
       DTO('optimize',
           lambda tmpl, tc: json_rtrip(tmpl._get_ast(optimize=True)),
           lambda tc: tc.opt_ast),
       DTO('compile', lambda tmpl, tc: tmpl._get_render_func(ret_str=True), None),
       DTO('render',
           lambda tmpl, tc: tmpl.render(tc.context or {}).strip(),
           lambda tc: tc.rendered.strip())]


class AshesTestResult(object):
    def __init__(self, test_case, env, lazy=True, raise_exc=False):
        self.name = test_case.name
        self.test_case = test_case
        self.env = env
        self.ops = [op for op in dir(self) if op.startswith('_test_')]
        self.raise_exc = raise_exc
        if not lazy:
            self.run()

    def run(self, raise_exc=None):
        if raise_exc is None:
            raise_exc = self.raise_exc

        self.results = []
        tmpl = self.env.load(self.name)
        tc = self.test_case
        skip_rest = False
        for op_name, get_result, get_ref in OPS:
            res, ref, tres = None, None, None
            try:
                if skip_rest:
                    continue
                if get_ref is not None:
                    ref = get_ref(tc)
                res = get_result(tmpl, tc)
                if get_ref is None:
                    tres = res is not None
                else:
                    if ref is None:
                        raise SkipTest()
                    else:
                        tres = (res == ref)
            except Exception as e:
                if isinstance(e, SkipTest):
                    tres = 'skipped'
                else:
                    res = tres = e
                    skip_rest = True
                    if raise_exc:
                        raise
            finally:
                self.results.append(DTR(op_name, res, ref, tres))

    def get_symbols(self):
        ret = []
        for result in self.results:
            if result.test_result == 'skipped':
                label = 'skipped'
            elif isinstance(result.test_result, Exception):
                label = 'error'
            elif result.test_result:
                label = 'passed'
            else:
                label = 'failed'
            ret.append(SYMBOLS[label])
        return ret
