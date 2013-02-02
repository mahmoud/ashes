from __future__ import unicode_literals

from collections import namedtuple, defaultdict, OrderedDict

from dust import DustEnv, ParseTree, Optimizer, tokenize
from tests import dust_site_tests
from tests.core import json_rtrip

DEFAULT_WIDTH = 70


class SkipTest(Exception):
    pass


def test_tokenize(test_case, env=None):
    if not test_case.template:
        raise SkipTest()
    return tokenize(test_case.template) is not None


def test_parse(test_case, env=None):
    p_tree = ParseTree.from_source(test_case.template)
    dust_ast = json_rtrip(p_tree.to_dust_ast())
    if not test_case.ast:
        raise SkipTest()
    return dust_ast == test_case.ast


def test_optimize(test_case, env=None):
    p_tree = ParseTree.from_source(test_case.template)
    dust_ast = json_rtrip(p_tree.to_dust_ast())
    opt_ast = json_rtrip(Optimizer().optimize(dust_ast))
    if not test_case.opt_ast:
        raise SkipTest()
    return opt_ast == json_rtrip(test_case.opt_ast)


def test_compile(test_case, env):
    return env.compile(test_case.template, test_case.name) is not None


def test_render(test_case, env):
    context = test_case.context or {}
    rendered = env.render(test_case.name, context)
    if test_case.rendered is None:
        raise SkipTest()
    return rendered.strip() == test_case.rendered.strip()


OPS = OrderedDict([('tokenize', test_tokenize),
                   ('parse', test_parse),
                   ('optimize', test_optimize),
                   ('compile', test_compile),
                   ('render', test_render)])


SYMBOLS = {'passed': '.', 'failed': 'X', 'skipped': '_', 'error': 'E'}


def get_test_results(test_cases, env=None):
    env = env or DustEnv()
    by_op = defaultdict(dict)
    by_test = defaultdict(dict)
    failed_memo = set()
    for op_name, op_func in OPS.items():
        for tc in test_cases:
            try:
                if tc.name in failed_memo:
                    raise SkipTest()
                elif op_func(tc, env):
                    res = 'passed'
                else:
                    res = 'failed'
            except SkipTest:
                res = 'skipped'
            except Exception as e:
                res = 'error'
                failed_memo.add(tc.name)
            by_op[op_name][tc.name] = res
            by_test[tc.name][op_name] = res

    return by_op, by_test


def get_heading_line(title='', width=DEFAULT_WIDTH, op_names=None):
    if op_names is None:
        op_names = OPS.keys()
    if len(title) > 20:
        title = title[:17] + '...'
    rwidth = width - 20

    pw = rwidth / len(op_names)
    tmpl = '{title:^20}' + ('{:^{pw}}' * len(op_names))
    return tmpl.format(title=title, pw=pw, *op_names)


def get_result_line(results, name='', width=DEFAULT_WIDTH):
    if len(name) > 20:
        name = name[:17] + '...'
    rwidth = width - 20

    pw = rwidth / len(results)

    tmpl = '{title:>20}' + ('{:^{pw}}' * len(results))
    return tmpl.format(title=name, pw=pw, *results)


def main(width=DEFAULT_WIDTH):
    lines = []
    headings = get_heading_line('Dust.js site refs')
    lines.append(headings)
    rstripped_width = len(headings.rstrip())
    lines.append('-' * (rstripped_width + 1))

    by_op, by_test = get_test_results(dust_site_tests)
    for tc in dust_site_tests:
        tc_name = tc.name
        res_symbols = []
        for op_name in OPS:
            res_symbols.append(SYMBOLS.get(by_test[tc_name][op_name]))
        lines.append(get_result_line(res_symbols, tc_name))
    print
    print '\n'.join(lines)
    print


if __name__ == '__main__':
    main()
