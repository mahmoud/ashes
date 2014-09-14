from __future__ import unicode_literals

from .core import AshesTest

heading = 'New features'


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
