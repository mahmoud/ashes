from __future__ import unicode_literals

import re
import cgi
import urllib
from pprint import pprint
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
path_re = re.compile(key_re_str + '?(\.' + key_re_str + ')+')

#comment_re = ''  # TODO
def strip_comments(text):
    return re.sub(r'\{!.+?!\}', '', text, flags=re.DOTALL).strip()


def get_path_or_key(pork):
    if pork == '.':
        pk = ('path', True, [])
    elif path_re.match(pork):
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


ALL_ATTRS = ('closing', 'symbol', 'refpath', 'contpath',
             'filters', 'params', 'selfclosing')


class Tag(object):
    req_attrs = ()
    ill_attrs = ()

    def __init__(self, **kw):
        self.match_str = kw.pop('match_str')
        self.__dict__.update(kw)
        if callable(getattr(self, 'check', None)):
            self.check()

    def check(self, raise_exc=True):  # todo: necessary?
        cn = self.__class__.__name__
        all_attrs = getattr(self, 'all_attrs', ())
        if all_attrs:
            req_attrs = [a for a in ALL_ATTRS if a in all_attrs]
            ill_attrs = [a for a in ALL_ATTRS if a not in all_attrs]
        else:
            req_attrs = getattr(self, 'req_attrs', ())
            ill_attrs = getattr(self, 'ill_attrs', ())

        opt_attrs = getattr(self, 'opt_attrs', ())
        if opt_attrs:
            ill_attrs = [a for a in ill_attrs if a not in opt_attrs]
        for attr in req_attrs:
            if getattr(self, attr, None) is None:
                raise ValueError('%s expected %s' % (cn, attr))
        for attr in ill_attrs:
            if getattr(self, attr, None) is not None:
                raise ValueError('%s does not take %s' % (cn, attr))
        return True

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r)' % (cn, self.match_str)

    @classmethod
    def from_match(cls, match):
        groups = match.groupdict()
        kw = dict([(k, v) for k, v in groups.items()
                   if v is not None])
        kw['match_str'] = match.group(0)
        obj = cls(**kw)
        obj.orig_match = match
        return obj


class BlockTag(Tag):
    all_attrs = ('contpath',)


class ReferenceTag(Tag):
    all_attrs = ('refpath',)
    opt_attrs = ('filters',)


class SectionTag(Tag):
    ill_attrs = ('closing')


class ClosingTag(Tag):
    all_attrs = ('closing', 'refpath')


class SpecialTag(Tag):
    all_attrs = ('symbol', 'refpath')


class BlockTag(Tag):
    all_attrs = ('symbol', 'refpath')


class PartialTag(Tag):
    req_attrs = ('symbol', 'refpath', 'selfclosing')


def get_tag(match):
    groups = match.groupdict()
    symbol = groups['symbol']
    closing = groups['closing']
    refpath = groups['refpath']
    if closing:
        tag_type = ClosingTag
    elif symbol is None and refpath is not None:
        tag_type = ReferenceTag
    elif symbol in '#?^<+@%':
        tag_type = SectionTag
    elif symbol == '~':
        tag_type = SpecialTag
    elif symbol == ':':
        tag_type = BlockTag
    elif symbol == '>':
        tag_type = PartialTag
    else:
        raise ValueError('invalid tag')
    return tag_type.from_match(match)


class BufferToken(object):
    def __init__(self, text=''):
        self.text = text

    def __repr__(self):
        disp = self.text
        if len(self.text) > 30:
            disp = disp[:30] + '...'
        return u'BufferToken(%r)' % disp


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
            tokens.append(BufferToken(source[prev_end:start]))
        prev_end = end
        tag = get_tag(match)
        tokens.append(tag)

    tail = source[prev_end:]
    if tail:
        tokens.append(BufferToken(tail))
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
