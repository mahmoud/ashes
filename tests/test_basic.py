from nose.tools import eq_
from dust import dust

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

TMP_OUTPUT = None
def test_basic():
    def callback(exception, content):
        global TMP_OUTPUT
        if exception:
            raise Exception(exception)
        TMP_OUTPUT = content
        return

    for name, tmpl in BASIC_TMPLS.items():
        dust.compile(tmpl, name)
        dust.render(name, INPUTS, callback)
        yield eq_, TMP_OUTPUT, BASIC_OUTPUTS[name]
