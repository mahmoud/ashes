from __future__ import unicode_literals

import re
import json
from collections import OrderedDict

__all__ = ['AshesTest']

_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))


class AshesTest(object):
    template = None
    json_ast = None
    json_opt_ast = None
    json_context = None
    rendered = None

    @property
    def name(self):
        return camel2under(self.__class__.__name__)

    @property
    def context(self):
        try:
            return json.loads(self.json_context)
        except:
            return None

    @property
    def ast(self):
        return json.loads(self.json_ast)

    @property
    def opt_ast(self):
        return json.loads(self.json_ast)


from ref_templates import ref_templates
from ref_asts import ref_asts
from ref_opt_asts import ref_opt_asts
from ref_renders import ref_renders
from ref_contexts import ref_contexts


def json_rtrip(obj, raise_exc=False):
    try:
        if isinstance(obj, basestring):
            return json.dumps(json.loads(obj))
        return json.loads(json.dumps(obj))
    except:
        if raise_exc:
            raise
        return obj


def generate_test(tmpl_name):
    tn = tmpl_name
    lines = ['class %s(AshesTest):' % under2camel(tmpl_name)]
    if tn in ref_templates:
        lines.append('template = %r' % ref_templates[tn])
    if tn in ref_asts:
        lines.append('json_ast = %r' % json_rtrip(ref_asts[tn]))
    if tn in ref_opt_asts:
        lines.append('json_opt_ast = %r' % json_rtrip(ref_opt_asts[tn]))
    if tn in ref_contexts:
        lines.append('json_context = %r' % json_rtrip(ref_contexts[tn]))
    if tn in ref_renders:
        lines.append('rendered = %r' % ref_renders[tn])
    if not lines:
        lines.append('pass')
    return '\n    '.join(lines)


def generate_tests():
    all_known = ref_templates.keys() + ref_asts.keys() + \
        ref_opt_asts.keys() + ref_renders.keys() + ref_contexts.keys()
    all_known = sorted(list(set(all_known)))
    gen_pairs = []
    for tmpl_name in all_known:
        gen_pairs.append((tmpl_name, generate_test(tmpl_name)))
    gen_pairs.sort(key=lambda x: len(x[1]))
    return OrderedDict(gen_pairs)


if __name__ == '__main__':
    for name, cls_str in generate_tests().items():
        print
        print cls_str
        print
