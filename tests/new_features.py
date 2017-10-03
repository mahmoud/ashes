from __future__ import unicode_literals

import unittest

import ashes
from .core import AshesTest

heading = 'new_features'


class raw_text(AshesTest):
    template = '{thing} {`{preserved} \n{whitespace} {#etc.}   `}'
    json_ast = r'["body", ["reference", ["key", "thing"], ["filters"]], ["buffer", " "], ["raw", "{preserved} \n{whitespace} {#etc.}   "]]'
    json_context = '{"thing": 123}'
    rendered = '123 {preserved} \n{whitespace} {#etc.}   '


class iter_lists_nosort(AshesTest):
    template = ('{@iterate key=lol}({$0}:{$1}:{$2}){/iterate}')
    json_context = '{"lol": [[1, 10, 100], [1, 2, 3], [4, 5, 6]]}'
    rendered = '(1:10:100)(1:2:3)(4:5:6)'


class iter_lists_asc(AshesTest):
    template = ('{@iterate sort="asc" sort_key=2 key=lol}'
                '({$0}:{$1}:{$2}){/iterate}')
    json_context = '{"lol": [[1, 10, 100], [1, 2, 3], [4, 5, 6]]}'
    rendered = '(1:2:3)(4:5:6)(1:10:100)'


class iter_lists_desc(AshesTest):
    template = ('{@iterate sort="desc" sort_key=2 key=lol}'
                '({$0}:{$1}:{$2}){/iterate}')
    json_context = '{"lol": [[1, 10, 100], [1, 2, 3], [4, 5, 6]]}'
    rendered = '(1:10:100)(4:5:6)(1:2:3)'


class iter_dicts(AshesTest):
    template = ('{@iterate sort="desc" sort_key="$key" key=lol}'
                '({$key}:{$value}){/iterate}')
    json_context = '{"lol": {"a": "alpha", "b": "beta", "c":"carotene"}}'
    rendered = '(c:carotene)(b:beta)(a:alpha)'


class select_no_body(AshesTest):
    template = '{@select key="foo"/}'
    json_context = '{}'
    rendered = ''


class select_const_eq(AshesTest):
    template = '{@select key="foo"}{@eq value="foo"}foo{/eq}{/select}'
    json_context = '{}'
    rendered = ''


class select_var_eq(AshesTest):
    template = '{@select key="foo"}{@eq value=10}foobar{/eq}{/select}'
    json_context = '{"foo": 10}'
    rendered = 'foobar'


class select_var_lt(AshesTest):
    template = '{@select key="foo"}{@lt value=20}foobar{/lt}{/select}'
    json_context = '{"foo": 10}'
    rendered = 'foobar'


class select_var_2_eq(AshesTest):
    template = ('{@select key="foo"}'
                '{@eq value="bar"}foobar{/eq}{@eq value="baz"}foobaz{/eq}'
                '{/select}')
    json_context = '{"foo": "baz"}'
    rendered = 'foobaz'


class select_var_2_var_eq(AshesTest):
    template = ('{@select key=test type="string"}'
                '{@eq value="{y}"}<div>FOO</div>{/eq}'
                '{@eq value="{x}"}<div>BAR</div>{/eq}'
                '{/select}')
    json_context = {"test": 42, "y": 42, "x": "bar"}
    rendered = ''  # TODO: this should be '<div>FOO</div>'
    # TODO (cont.) but we don't support subtemplating in this manner "{x}"


class select_var_3_default(AshesTest):
    template = ('{@select key=foo}'
                '{@eq value="bar"}foobar{/eq}'
                '{@eq value="baz"}foobaz{/eq}'
                '{@eq value="foobar"}foofoobar{/eq}'
                '{@none value="foo"}foofoo{/none}'
                '{/select}')
    json_context = {"foo": "foo"},
    rendered = "foofoo"


class select_var_no_key(AshesTest):
    template = ('{#b}{@select}'
                '{@eq key=x value=z}FOO{/eq}'
                '{@eq key=x value=x}BAR{/eq}'
                '{@none}foofoo{/none}'
                '{/select}{/b}')
    json_context = '{"b": {"z": "foo", "x": "bar"}}'
    rendered = 'BAR'


# class select_var_key_path(AshesTest):
#    template = ('{@select key=x.key}{@eq value=10}foobar{/eq}{/select}')
#    json_context = '{"x": {"key": 10}}'
#    rendered = 'foobar'

class select_undefined_key(AshesTest):
    template = ('{#b}{@select key=y}'
                '{@eq value=z}FOO{/eq}'
                '{@eq value=x}BAR{/eq}'
                '{@none}foofoo{/none}'
                '{/select}{/b}')
    json_context = '{"b": {"z": "foo", "x": "bar"}}'
    rendered = 'foofoo'


class select_bool_coerce(AshesTest):
    template = ('{@select key=not_there}'
                '{@eq value="true" type="boolean"}all the messages{/eq}'
                '{@eq value="false" type="boolean"}no messages{/eq}'
                '{/select}')
    json_context = '{}'
    rendered = 'no messages'


#class select_inside_loop(AshesTest):
#    template = ("{#skills}{@select key=.}"
#                '{@eq value="c"}C, {/eq}'
#                "{@eq value=\"python\"}python, {/eq}"
#                "{@none}{.|ppjson|s} {/none}"
#                "{/select}{/skills}")
#    json_context = '{"skills": ["c", "python", "and more"]}'
#    rendered = "C, python, and more"
#
# TODO: issue with above is that key should be "{.}". in select_helper
# params.get("key") is the resolved value, and it's not clear that the
# value isn't itself a key in the context.


class EnvDefaultsTest(unittest.TestCase):
    def setUp(self):
        self.env = ashes.AshesEnv(defaults={'baz': 3})
        self.env.register_source('basic_defaults_tmpl',
                                 '{foo} {bar} {baz} {blep}.')

    def test_basic_defaults(self):
        res = self.env.render('basic_defaults_tmpl', {'foo': 1, 'bar': 2})
        assert res == '1 2 3 .'
