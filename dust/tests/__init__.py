from __future__ import unicode_literals

import re

__all__ = ['AshesTest']

_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(string):
    return _camel2under_re.sub(r'_\1', string).lower()


def under2camel(string):
    return ''.join(w.capitalize() or '_' for w in string.split('_'))


class AshesTest(object):
    template = None
    ast = None
    optimized_ast = None
    context = None
    rendered = None


from ref_templates import ref_templates
from ref_asts import ref_asts
from ref_opt_asts import ref_opt_asts
from ref_renders import ref_renders
from ref_contexts import ref_contexts


def generate_test(tmpl_name):
    pass


def generate_tests():
    all_known = ref_templates.keys() + ref_asts.keys() + \
        ref_opt_asts.keys() + ref_renders.keys() + ref_contexts.keys()
    all_known = sorted(list(set(all_known)))
    return all_known


if __name__ == '__main__':
    t = generate_tests()
    print len(t), 'known tests', t
