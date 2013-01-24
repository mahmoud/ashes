from __future__ import unicode_literals

import re
import cgi
import urllib


node_re = re.compile(r'({(?P<symbol>[\~\#\?\@\:\<\>\+\/\^])?'
                     r'(?P<refpath>[a-zA-Z0-9_\$\.]+|"[^"]+")'
                     r'(?:\:(?P<contpath>[a-zA-Z0-9\$\.]+))?'
                     r'(?P<filters>\|[a-z]+)*?'
                     r'( \w+\=(("[^"]*?")|([\w\.]+)))*?\/?\})',
                     flags=re.MULTILINE)


#comment_re = ''  # TODO
def strip_comments(text):
    return re.sub(r'\{!.+?!\}', '', text, flags=re.DOTALL).strip()


def decompose_tag(match):
    ret = ['{']
    symbol = match.group('symbol')
    if symbol:
        ret.append(symbol)
    refpath = match.group('refpath')
    if refpath:
        ret.append(('path', refpath))
    ret.append('}')
    return ret


_BUFFER = 'buffer'
_TAG = 'TAG'
def tokenize(source):
    # removing comments
    source = strip_comments(source)
    tokens = []
    prev_end = 0
    start = None
    end = None
    for match in node_re.finditer(source):
        start, end = match.start(1), match.end(1)
        if prev_end < start:
            tokens.append((_BUFFER, source[prev_end:start]))
        prev_end = end
        tokens.extend(decompose_tag(match))
    tail = source[prev_end:]
    if tail:
        tokens.append((_BUFFER, tail))
    return tokens


def escape_html(text):
    text = unicode(text)
    return cgi.escape(text, True).replace("'", '&squot;')


def escape_js(text):
    text = unicode(text)
    return (text
            .replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace("'", "\\'")
            .replace('\r', '\\r')
            .replace('\u2028', '\\u2028')
            .replace('\u2029', '\\u2029')
            .replace('\n', '\\n')
            .replace('\f', '\\f')
            .replace('\t', '\\t'))


def escape_uri(text):
    return urllib.quote(text)


def escape_uri_component(text):
    return (escape_uri(text)
            .replace('/', '%2F')
            .replace('?', '%3F')
            .replace('=', '%3D')
            .replace('&', '%26'))


class Template(object):
    pass


class DustEnv(object):
    default_filters = {
        'h': escape_html,
        'j': escape_js,
        'u': escape_uri,
        'uc': escape_uri_component}

    def __init__(self):
        self.templates = {}
        self.filters = dict(self.default_filters)

    def compile(self, string, name, src_file=None):
        pass

    def load(self, src_file, name=None):
        if name is None:
            name = src_file
        if src_file in self.templates:
            return self.templates[name].root_node
        else:
            with open(src_file, 'r') as f:
                code = f.read()
            return self.compile(code, name, src_file=src_file)

    def render(self, name, model):
        try:
            template = self.templates[name]
        except KeyError:
            raise ValueError('No template named "%s"' % name)

        return template.render(model, env=self)


#dust = default_env = DustEnv()
