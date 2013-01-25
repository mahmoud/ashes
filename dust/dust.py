from __future__ import unicode_literals

import re
import cgi
import urllib

node_re_o = re.compile(r'({(?P<symbol>[\~\#\?\@\:\<\>\+\/\^])?'
                       r'(?P<refpath>[a-zA-Z0-9_\$\.]+|"[^"]+")'
                       r'(?:\:(?P<contpath>[a-zA-Z0-9\$\.]+))?'
                       r'(?P<filters>\|[a-z]+)*?'
                       r'( \w+\=(("[^"]*?")|([\w\.]+)))*?\/?\})',
                       flags=re.MULTILINE)

# need to add group for literals
# switch to using word boundary for params section
node_re = re.compile(r'({'
                     r'(?P<closing>\/)?'
                     r'(?P<symbol>[\~\#\?\@\:\<\>\+\^])?'
                     r'(?P<refpath>[a-zA-Z0-9_\$\.]+|"[^"]+")'
                     r'(?:\:(?P<contpath>[a-zA-Z0-9\$\.]+))?'
                     r'(?P<filters>\|[a-z]+)*?'
                     r'(?P<params> \w+\=(("[^"]*?")|([\w\.]+)))*?'
                     r'(?P<selfclosing>\/)?'
                     r'\})',
                     flags=re.MULTILINE)

key_re_str = '[a-zA-Z_$][0-9a-zA-Z_$]*'
key_re = re.compile(key_re_str)
path_re = re.compile(key_re_str+'?(\.'+key_re_str+')+')

#comment_re = ''  # TODO
def strip_comments(text):
    return re.sub(r'\{!.+?!\}', '', text, flags=re.DOTALL).strip()


def get_path_or_key(pork):
    if path_re.match(pork):
        f_local = pork.startswith('.')
        pk = ('path', f_local, pork.split('.'))
    elif key_re.match(pork):
        pk = ('key', pork)
    else:
        raise ValueError('expected a path or key, not %r' % pork)
    return pk


def params_to_kv(params_str):
    ret = []
    new_k, v = None, None
    k, _, tail = params_str.partition('=')
    while tail:
        tmp, _, tail = tail.partition('=')
        if not tail:
            v = tmp
        else:
            v, new_k = tmp.split()
        ret.append((k.strip(), v.strip()))
        k = new_k
    return ret


def wrap_params(param_kv):
    ret = []
    for k, v in param_kv:
        # i know this isn't right, it's just for a second
        ret.append(('param', ('literal', k), ('literal', v)))
    return ret


def decompose_tag(match):
    ret = []
    is_closing = match.group('closing') is not None
    is_selfclosing = match.group('selfclosing') is not None
    symbol = match.group('symbol')
    refpath = match.group('refpath')
    if refpath:
        pk = get_path_or_key(refpath)
    contpath = match.group('contpath')
    if contpath:
        cont_pk = get_path_or_key(contpath)
    params_str = match.group('params')
    if params_str:
        params_kv = params_to_kv(params_str)
        params = wrap_params(params_kv)

    if is_closing:
        ret.append('/')
    if symbol:
        ret.append(symbol)  # context, params
    if refpath:
        ret.append(pk)
    if contpath:
        ret.extend((':', cont_pk))
    if params_str:
        ret.append(['params'] + params)
    if is_selfclosing:
        ret.append('/')
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
        d_tag = decompose_tag(match)
        tokens.extend(d_tag)
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
