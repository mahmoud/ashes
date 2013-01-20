# -*- coding: utf-8 -*-
from nose.tools import eq_
from dust import dust, DustEnv

BASIC_TMPLS = {
    'plain':       'Hello World!',
    'replace':     'Hello {name}! You have {count} new messages.',
    'zero':        '{#zero}{.}{/zero}',
    'array':       '{#names}{title} {name}{~n}{/names}',
    'empty_array': '{#empty_array}{title} {name}{~n}{/empty_array}',
    'implicit':    '{#names}{.}{~n}{/names}'
    }

BASIC_OUTPUTS = {
    'plain':       'Hello World!',
    'replace':     'Hello Kurt! You have 30 new messages.',
    'zero':        '0',
    'array':       'Sir Moe\nSir Larry\nSir Curly\n',
    'empty_array': '',
    'implicit':    'Moe\nLarry\nCurly\n',
    }

INPUTS = {
    'name': 'Kurt',
    'count': 30,
    'zero': 0,
    'title': 'Sir',
    'names': [{'name': 'Moe'}, {'name': 'Larry'}, {'name': 'Curly'}],
    'empty_array': [],
    }


def the_basics(dust_env):
    for name, tmpl in BASIC_TMPLS.iteritems():
        dust_env.compile(tmpl, name)
        output = dust_env.render(name, INPUTS)
        yield eq_, output, BASIC_OUTPUTS[name]


def test_default_env():
    for t in the_basics(dust):
        yield t


def test_manual_env():
    dust = DustEnv()
    for t in the_basics(dust):
        yield t
