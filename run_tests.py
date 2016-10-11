#!/usr/bin/env python
from __future__ import unicode_literals, print_function

from pprint import pformat
try:
    from collections import OrderedDict
    from argparse import ArgumentParser
except ImportError:
    # Python 2.6 stuff
    from tests.OrderedDict import OrderedDict
    from tests.argparse import ArgumentParser

import tests
from ashes import AshesEnv, Template
from tests import ALL_TEST_MODULES, OPS, AshesTest
import unittest

DEFAULT_WIDTH = 70

LEGEND = '. = passed, _ = skipped, X = failed, E = exception'

import sys
PY3 = (sys.version_info[0] == 3)
if PY3:
    unicode = str
    basestring = str


def get_line(title, items, twidth=20, talign='>', width=DEFAULT_WIDTH):
    if len(title) > twidth:
        title = title[:twidth - 3] + '...'
    rwidth = width - twidth
    items = list(items or [])
    pw = int(rwidth / len(items))
    item_tmpl = ''.join(['{' + str(i) + ':^{pw}}' for i in range(len(items))])
    tmpl = '{title:{talign}{twidth}}' + item_tmpl
    return tmpl.format(title=title,
                       talign=talign,
                       twidth=twidth,
                       pw=pw,
                       *items)


def get_unit_tests(module):
    tests = [t for t in module.__dict__.values()
             if isinstance(t, type) and issubclass(t, unittest.TestCase) and
             t is not unittest.TestCase]
    return tests


def get_sorted_tests(module):
    tests = [t for t in module.__dict__.values()
             if hasattr(t, 'ast') and issubclass(t, AshesTest) and
             t is not AshesTest]
    return sorted(tests, key=lambda x: len(x.template or ''))


def get_test_results(test_cases, raise_on=None):
    env = AshesEnv(keep_whitespace=False)
    ret = []
    for tc in test_cases:
        if issubclass(tc, AshesTest):
            env.register(Template(tc.name, tc.template, env=env, lazy=True))
    for tc in test_cases:
        if issubclass(tc, AshesTest):
            raise_exc = (tc.name == raise_on)
            ret.append(tc.get_test_result(env, raise_exc=raise_exc))
    return ret


def get_grid(test_results, title, width=DEFAULT_WIDTH):
    lines = ['', '  ' + LEGEND, '']

    if test_results:
        test_count = len(test_results)
        col_names = [dt.op_name for dt in OPS]
        headings = get_line(title, col_names, talign='^')
        lines.append(headings)
        rstripped_width = len(headings.rstrip())
        bar_str = '-' * (rstripped_width + 1)
        lines.append(bar_str)

        counters = OrderedDict([(cn, 0) for cn in col_names])
        for tres in test_results:
            lines.append(get_line(tres.name, tres.get_symbols()))
            for dtr in tres.results:
                if dtr.test_result is True:
                    counters[dtr.op_name] += 1
        lines.append(bar_str)
        lines.append(get_line('(%s total)' % test_count, counters.values()))

    else:
        lines.append('No tests found.')
    return '\n'.join(lines + [''])


def get_single_report(name, op=None, verbose=None, debug=None):
    raise_on = None
    mod_name, _, test_name = name.rpartition('.')
    test_module = getattr(tests, mod_name or 'dust_site')
    lookup = dict([(k.lower(), v) for k, v in test_module.__dict__.items()])
    try:
        test = lookup[test_name.lower()]
    except KeyError:
        print('No test named: %r' % name)
        return

    if debug:
        raise_on = test.name

    try:
        tres = get_test_results([test], raise_on)[0]
    except Exception as e:
        print(e)
        import pdb
        pdb.post_mortem()
        raise

    lines = []
    for op_name, result, result_ref, test_result in tres.results:
        if not verbose and (test_result is True or test_result == 'skipped'):
            continue
        if op:
            if op_name != op:
                continue
        else:
            lines.append('')
        lines.append(' * %s %s reference:' % (name, op_name))
        if not isinstance(result_ref, basestring):
            result_ref = pformat(result_ref)
        lines.extend(['----', result_ref, '----', ''])
        lines.append(' * %s %s actual:' % (name, op_name))
        if not isinstance(result, basestring):
            result = pformat(result)
        lines.extend(['----', result, '----'])
    if not lines:
        lines = ['No results found for test: %r' % name]
    else:
        lines = ['', 'Test results for %r' % name] + lines
    return '\n'.join(lines)


def parse_args():
    prs = ArgumentParser(description="command central for developing and"
                         " testing Ashes.")
    prs.add_argument('--name', help='see results for this test case')
    prs.add_argument('--op', help='only see test result for this operation')
    prs.add_argument('--verbose', action='store_true',
                     help='also show results of passing ops')
    prs.add_argument('--debug', action='store_true',
                     help='pop a pdb.post_mortem() on exceptions')
    prs.add_argument('--benchmark', action='store_true',
                     help='run benchmarks')
    prs.add_argument('--run_unittests', action='store_true',
                     help='run unittests')

    return prs.parse_args()


def main(width=DEFAULT_WIDTH):
    args = parse_args()
    name = args.name

    run_benchmarks = args.benchmark or False
    run_unittests = args.run_unittests or False
    if not name:
        # remember `tests` is a namespace. don't overwrite!
        for test_mod in ALL_TEST_MODULES:
            title = getattr(test_mod, 'heading', '')
            _tests = get_sorted_tests(test_mod)
            test_results = get_test_results(_tests)
            grid = get_grid(test_results, title)
            if grid:
                print(test_mod)
                print(grid)
        # do we have unittests?
        if run_unittests:
            _unit_tests = []
            for test_mod in ALL_TEST_MODULES:
                _tests = get_unit_tests(test_mod)
                if _tests:
                    _unit_tests.extend(_tests)
            if _unit_tests:
                loader = unittest.TestLoader()
                suites_list = []
                for _test in _unit_tests:
                    suite = loader.loadTestsFromTestCase(_test)
                    suites_list.append(suite)
                big_suite = unittest.TestSuite(suites_list)
                runner = unittest.TextTestRunner(verbosity=3)
                results = runner.run(big_suite)
        # toggled!
        if run_benchmarks:
            tests.benchmarks.bench_render_a()
            tests.benchmarks.bench_cacheable_templates()
    else:
        single_rep = get_single_report(name, args.op, args.verbose, args.debug)
        if single_rep:
            print(single_rep)


if __name__ == '__main__':
    main()
