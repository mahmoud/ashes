from __future__ import unicode_literals

from .core import AshesTest

heading = 'New features'


class raw_text(AshesTest):
    template = '{thing} {`{preserved} \n{whitespace} {#etc.}   `}'
    json_ast = r'["body", ["reference", ["key", "thing"], ["filters"]], ["buffer", " "], ["raw", "{preserved} \n{whitespace} {#etc.}   "]]'
    json_context = '{"thing": 123}'
    rendered = '123 {preserved} \n{whitespace} {#etc.}   '
