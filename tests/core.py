from __future__ import unicode_literals

import re
import json
from collections import OrderedDict

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


###########################
# Test result stuff follows
###########################


class SkipTest(Exception):
    pass


def _test_tokenize(tmpl, tc=None, env=None):
    return tmpl._get_tokens() is not None


def _test_parse(tmpl, tc, env=None):
    dust_ast = json_rtrip(tmpl._get_ast(raw=True))
    if not tc.ast:
        raise SkipTest()
    return dust_ast == tc.ast


def _test_optimize(tmpl, tc, env=None):
    dust_opt_ast = json_rtrip(tmpl._get_ast(optimize=True))
    if not tc.opt_ast:
        raise SkipTest()
    return dust_opt_ast == json_rtrip(tc.opt_ast)


def _test_compile(tmpl, tc, env=None):
    return callable(tmpl._get_render_func())


def _test_render(tmpl, tc, env):
    context = tc.context or {}
    rendered = tmpl.render(context)
    if tc.rendered is None:
        raise SkipTest()
    return rendered.strip() == tc.rendered.strip()


OPS = OrderedDict([('tokenize', _test_tokenize),
                   ('parse', _test_parse),
                   ('optimize', _test_optimize),
                   ('compile', _test_compile),
                   ('render', _test_render)])


SYMBOLS = {'passed': '.', 'failed': 'X', 'skipped': '_', 'error': 'E'}

class AshesTest(object):
    template = None
    json_ast = None
    json_opt_ast = None
    json_context = None
    rendered = None

    __metaclass__ = ATMeta

    @classmethod
    def get_test_result(cls, env):
        res_kwargs = {}
        tmpl = env.load(cls.name)
        for op_name, op_func in OPS.items():
            try:
                if op_func(tmpl, cls, env):
                    res = 'passed'
                else:
                    res = 'failed'
            except SkipTest:
                res = 'skipped'
            except Exception as e:
                res = e
                break
            finally:
                res_kwargs[op_name] = res
        return AshesTestResult(cls, **res_kwargs)


class AshesTestResult(object):
    def __init__(self, test_case, **kwargs):
        self.name = test_case.name
        self.test_case = test_case
        self.results = OrderedDict()
        for op_name in OPS:
            self.results[op_name] = kwargs.get(op_name, 'skipped')
        self.symbols = []
        for op_name, result in self.results.items():
            if isinstance(result, Exception):
                result = 'error'
            self.symbols.append(SYMBOLS[result])


def json_rtrip(obj, raise_exc=False):
    try:
        if isinstance(obj, basestring):
            return json.dumps(json.loads(obj))
        return json.loads(json.dumps(obj))
    except:
        if raise_exc:
            raise
        return obj
