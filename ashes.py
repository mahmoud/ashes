from __future__ import unicode_literals

import re
import cgi
import json
import urllib

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
path_re = re.compile('(' + key_re_str + ')?(\.' + key_re_str + ')+')


#comment_re = ''  # TODO
def strip_comments(text):
    return re.sub(r'\{!.+?!\}', '', text, flags=re.DOTALL)


def get_path_or_key(pork):
    if pork == '.':
        pk = ('path', True, [])
    elif path_re.match(pork):
        f_local = pork.startswith('.')
        if f_local:
            pork = pork[1:]
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
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
            v_tuple = ('literal', v)
        else:
            v_tuple = get_path_or_key(v)
        ret.append(('param', ('literal', k), v_tuple))
    return ret


ALL_ATTRS = ('closing', 'symbol', 'refpath', 'contpath',
             'filters', 'params', 'selfclosing')


class Tag(object):
    req_attrs = ()
    ill_attrs = ()

    def __init__(self, **kw):
        self.match_str = kw.pop('match_str')
        self._attr_dict = kw
        self.set_attrs(kw)

    @property
    def param_list(self):
        try:
            return params_to_kv(self.params)
        except AttributeError:
            return []

    def set_attrs(self, attr_dict, raise_exc=True):
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
            if attr_dict.get(attr, None) is None:
                raise ValueError('%s expected %s' % (cn, attr))
        for attr in ill_attrs:
            if attr_dict.get(attr, None) is not None:
                raise ValueError('%s does not take %s' % (cn, attr))

        avail_attrs = [a for a in ALL_ATTRS if a not in ill_attrs]
        for attr in avail_attrs:
            setattr(self, attr, attr_dict.get(attr, ''))
        return True

    def __repr__(self):
        cn = self.__class__.__name__
        return '%s(%r)' % (cn, self.match_str)

    @classmethod
    def from_match(cls, match):
        kw = dict([(k, v) for k, v in match.groupdict().items()
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

    def to_dust_ast(self):
        pork = get_path_or_key(self.refpath)
        filters = ['filters']
        if self.filters:
            f_list = self.filters.split('|')[1:]
            for f in f_list:
                filters.append(f)
        return [['reference', pork, filters]]


class SectionTag(Tag):
    ill_attrs = ('closing')


class ClosingTag(Tag):
    all_attrs = ('closing', 'refpath')


class SpecialTag(Tag):
    all_attrs = ('symbol', 'refpath')

    def to_dust_ast(self):
        return [['special', self.refpath]]


class BlockTag(Tag):
    all_attrs = ('symbol', 'refpath')


class PartialTag(Tag):
    req_attrs = ('symbol', 'refpath', 'selfclosing')

    def __init__(self, **kw):
        super(PartialTag, self).__init__(**kw)
        self.subtokens = parse_inline(self.refpath)

    def to_dust_ast(self):
        context = ['context']
        contpath = self.contpath
        if contpath:
            context.append(get_path_or_key(contpath))
        subtokens = self.subtokens
        if subtokens and isinstance(subtokens[0], BufferToken):
            body = ['literal', subtokens[0].text]
        else:
            body = ['body']
            for b in self.subtokens:
                body.extend(b.to_dust_ast())
        return [['partial',
                 body,
                 context]]


def parse_inline(source):
    if not source:
        raise ValueError('empty inline token')
    orig_source = source
    if source.startswith('"') and source.endswith('"'):
        source = source[1:-1]
    if not source:
        return BufferToken()
    tokens = tokenize(source, inline=True)
    return tokens


def get_tag(match, inline=False):
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
    if inline and tag_type not in (ReferenceTag, SpecialTag):
        raise ValueError('invalid inline tag')
    return tag_type.from_match(match)


class WhitespaceToken(object):
    def __init__(self, ws=''):
        self.ws = ws

    def __repr__(self):
        disp = self.ws
        if len(disp) > 13:
            disp = disp[:10] + '...'
        return u'WhitespaceToken(%r)' % disp


def split_leading(text):
    leading_stripped = text.lstrip()
    leading_ws = text[:len(text) - len(leading_stripped)]
    return leading_ws, leading_stripped


class BufferToken(object):
    def __init__(self, text=''):
        self.text = text

    def __repr__(self):
        disp = self.text
        if len(self.text) > 30:
            disp = disp[:27] + '...'
        return u'BufferToken(%r)' % disp

    def to_dust_ast(self):
        # It is hard to simulate the PEG parsing in this case,
        # especially while supporting universal newlines.
        if not self.text:
            return []
        rev = []
        remaining_lines = self.text.splitlines()
        if self.text[-1] in ('\n', '\r'):
            # kind of a bug in splitlines if you ask me.
            remaining_lines.append('')
        while remaining_lines:
            line = remaining_lines.pop()
            leading_ws, lstripped = split_leading(line)
            if remaining_lines:
                if lstripped:
                    rev.append(['buffer', lstripped])
                rev.append(['format', '\n', leading_ws])
            else:
                if line:
                    rev.append(['buffer', line])
        ret = list(reversed(rev))
        return ret


def tokenize(source, inline=False):
    # TODO: line/column numbers
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
        tag = get_tag(match, inline)
        tokens.append(tag)
    tail = source[prev_end:]
    if tail:
        tokens.append(BufferToken(tail))
    return tokens


#########
# PARSING
#########

class Section(object):
    def __init__(self, start_tag=None, blocks=None):
        if start_tag is None:
            name = '<root>'
        else:
            name = start_tag.refpath
        self.name = name
        self.start_tag = start_tag
        self.blocks = blocks or []

    def add(self, obj):
        if type(obj) == Block:
            self.blocks.append(obj)
        else:
            if not self.blocks:
                self.blocks = [Block()]
            self.blocks[-1].add(obj)

    def to_dict(self):
        ret = {self.name: dict([(b.name, b.to_list()) for b in self.blocks])}
        return ret

    def to_dust_ast(self):
        symbol = self.start_tag.symbol
        key = self.start_tag.refpath

        context = ['context']
        contpath = self.start_tag.contpath
        if contpath:
            context.append(get_path_or_key(contpath))

        params = ['params']
        param_list = self.start_tag.param_list
        if param_list:
            params.extend(wrap_params(param_list))

        bodies = ['bodies']
        if self.blocks:
            for b in reversed(self.blocks):
                bodies.extend(b.to_dust_ast())

        return [[symbol,
                [u'key', key],
                context,
                params,
                bodies]]


class Block(object):
    def __init__(self, name='block'):
        if not name:
            raise ValueError('blocks need a name, not: %r' % name)
        self.name = name
        self.items = []

    def add(self, item):
        self.items.append(item)

    def to_list(self):
        ret = []
        for i in self.items:
            try:
                ret.append(i.to_dict())
            except AttributeError:
                ret.append(i)
        return ret

    def _get_dust_body(self):
        # for usage by root block in ParseTree
        ret = []
        for i in self.items:
            ret.extend(i.to_dust_ast())
        return ret

    def to_dust_ast(self):
        name = self.name
        body = ['body']
        dust_body = self._get_dust_body()
        if dust_body:
            body.extend(dust_body)
        return [['param',
                ['literal', name],
                body]]


class ParseTree(object):
    def __init__(self, root_block):
        self.root_block = root_block

    def to_dust_ast(self):
        ret = ['body']
        ret.extend(self.root_block._get_dust_body())
        return ret

    @classmethod
    def from_tokens(cls, tokens):
        root_sect = Section()
        ss = [root_sect]  # section stack
        for token in tokens:
            if type(token) == SectionTag:
                new_s = Section(token)
                ss[-1].add(new_s)
                if not token.selfclosing:
                    ss.append(new_s)
            elif type(token) == ClosingTag:
                if len(ss) <= 1:
                    raise ValueError('closing tag before opening tag: %r' % token)
                if token.refpath != ss[-1].start_tag.refpath:
                    raise ValueError('nesting error')
                ss.pop()
            elif type(token) == BlockTag:
                if len(ss) <= 1:
                    raise ValueError('cannot start blocks outside of a section')
                new_b = Block(name=token.refpath)
                ss[-1].add(new_b)
            else:
                ss[-1].add(token)
        return cls(root_sect.blocks[0])

    @classmethod
    def from_source(cls, src):
        tokens = tokenize(src)
        return cls.from_tokens(tokens)


##############
# Optimize AST
##############
DEFAULT_SPECIAL_CHARS = {'s': ' ',
                         'n': '\n',
                         'r': '\r',
                         'lb': '{',
                         'rb': '}'}

DEFAULT_OPTIMIZERS = {
    'body': 'compact_buffers',
    'special': 'convert_special',
    'format': 'nullify',
    'comment': 'nullify'}

for nsym in ('buffer', 'filters', 'key', 'path', 'literal'):
    DEFAULT_OPTIMIZERS[nsym] = 'noop'

for nsym in ('#', '?', '^', '<', '+', '@', '%', 'reference',
             'partial', 'context', 'params', 'bodies', 'param'):
    DEFAULT_OPTIMIZERS[nsym] = 'visit'

UNOPT_OPTIMIZERS = dict(DEFAULT_OPTIMIZERS)
UNOPT_OPTIMIZERS.update({'format': 'noop', 'body': 'visit'})


def escape(text, esc_func=json.dumps):
    return esc_func(text)


class Optimizer(object):
    def __init__(self, optimizers=None, special_chars=None):
        if special_chars is None:
            special_chars = DEFAULT_SPECIAL_CHARS
        self.special_chars = special_chars

        if optimizers is None:
            optimizers = DEFAULT_OPTIMIZERS
        self.optimizers = dict(optimizers)

    def optimize(self, node):
        # aka filter_node()
        nsym = node[0]
        optimizer_name = self.optimizers[nsym]
        return getattr(self, optimizer_name)(node)

    def noop(self, node):
        return node

    def nullify(self, node):
        return None

    def convert_special(self, node):
        return ['buffer', self.special_chars[node[1]]]

    def visit(self, node):
        ret = [node[0]]
        for n in node[1:]:
            filtered = self.optimize(n)
            if filtered:
                ret.append(filtered)
        return ret

    def compact_buffers(self, node):
        ret = [node[0]]
        memo = None
        for n in node[1:]:
            filtered = self.optimize(n)
            if not filtered:
                continue
            if filtered[0] == 'buffer':
                if memo is not None:
                    memo[1] += filtered[1]
                else:
                    memo = filtered
                    ret.append(filtered)
            else:
                memo = None
                ret.append(filtered)
        return ret

    def __call__(self, node):
        return self.optimize(node)


#########
# Compile
#########


ROOT_RENDER_TMPL = \
'''def render(chk, ctx):
    {body}
    return {root_func_name}(chk, ctx)
'''


def _python_compile(source, name, global_env=None):
    if global_env is None:
        global_env = {}
    else:
        global_env = dict(global_env)
    try:
        code = compile(source, '<string>', 'single')
    except:
        #print source
        raise
    exec code in global_env
    return global_env[name]


class Compiler(object):
    """
    Note: Compiler objects aren't really meant to be reused,
    the class is just for namespacing and convenience.
    """
    sections = {'#': 'section',
                '?': 'exists',
                '^': 'notexists'}
    nodes = {'<': 'inline_partial',
             '+': 'region',
             '@': 'helper',
             '%': 'pragma'}

    def __init__(self, env=None):
        if env is None:
            env = default_env
        self.env = env

        self.bodies = {}
        self.blocks = {}
        self.block_str = ''
        self.index = 0
        self.auto = 'h'  # TODO

    def compile(self, ast, name='render'):
        python_source = self._gen_python(ast)
        return _python_compile(python_source, name)

    def _gen_python(self, ast):  # ast to init?
        lines = []
        c_node = self._node(ast)

        block_str = self._root_blocks()

        bodies = self._root_bodies()
        lines.extend(bodies.splitlines())
        if block_str:
            lines.extend(['', block_str, ''])
        body = '\n    '.join(lines)

        ret = ROOT_RENDER_TMPL.format(body=body,
                                      root_func_name=c_node)
        self.python_source = ret
        return ret

    def _root_blocks(self):
        if not self.blocks:
            self.block_str = ''
            return ''
        self.block_str = 'ctx = ctx.shift_blocks(blocks)\n    '
        pairs = ['"' + name + '": ' + fn for name, fn in self.blocks.items()]
        return 'blocks = {' + ', '.join(pairs) + '}'

    def _root_bodies(self):
        max_body = max(self.bodies.keys())
        ret = [''] * (max_body + 1)
        for i, body in self.bodies.items():
            ret[i] = '\ndef body_%s(chk, ctx):\n    %sreturn chk%s\n' % (i, self.block_str, body)
        return ''.join(ret)

    def _convert_special(self, node):
        return ['buffer', self.special_chars[node[1]]]

    def _node(self, node):
        ntype = node[0]
        if ntype in self.sections:
            stype = self.sections[ntype]
            return self._section(node, stype)
        elif ntype in self.nodes:
            ntype = self.nodes[ntype]

        cfunc = getattr(self, '_' + ntype, None)
        if not callable(cfunc):
            raise TypeError('unsupported node type: "%r"', node[0])
        return cfunc(node)

    def _body(self, node):
        index = self.index
        self.index += 1   # make into property, equal to len of bodies?
        name = 'body_%s' % index
        self.bodies[index] = self._parts(node)
        return name

    def _parts(self, body):
        parts = []
        for part in body[1:]:
            parts.append(self._node(part))
        return ''.join(parts)

    def _buffer(self, node):
        return '.write(%s)' % escape(node[1])

    def _format(self, node):
        return '.write(%s)' % escape(node[1] + node[2])

    def _reference(self, node):
        return '.reference(%s,ctx,%s)' % (self._node(node[1]),
                                          self._node(node[2]))

    def _section(self, node, cmd):
        return '.%s(%s,%s,%s,%s)' % (cmd,
                                     self._node(node[1]),
                                     self._node(node[2]),
                                     self._node(node[4]),
                                     self._node(node[3]))

    def _inline_partial(self, node):
        bodies = node[4]
        for param in bodies[1:]:
            btype = param[1][1]
            if btype == 'block':
                self.blocks[node[1][1]] = self._node(param[2])
                return ''
        return ''

    def _region(self, node):
        """aka the plus sign ('+') block"""
        tmpl = '.block(ctx.get_block(%s),%s,%s,%s)'
        return tmpl % (escape(node[1][1]),
                       self._node(node[2]),
                       self._node(node[4]),
                       self._node(node[3]))

    def _helper(self, node):
        return '.helper(%s,%s,%s,%s)' % (escape(node[1][1]),
                                         self._node(node[2]),
                                         self._node(node[4]),
                                         self._node(node[3]))

    def _pragma(self, node):
        raise NotImplemented

    def _partial(self, node):
        if node[0] == 'body':
            body_name = self._node(node[1])
            return '.partial(' + body_name + ', %s)' % self._node(node[2])
        return '.partial(%s, %s)' % (self._node(node[1]),
                                     self._node(node[2]))

    def _context(self, node):
        contpath = node[1:]
        if contpath:
            return 'ctx.rebase(%s)' % (self._node(contpath[0]))
        return 'ctx'

    def _params(self, node):
        parts = [self._node(p) for p in node[1:]]
        if parts:
            return '{' + ','.join(parts) + '}'
        return 'None'

    def _bodies(self, node):
        parts = [self._node(p) for p in node[1:]]
        return '{' + ','.join(parts) + '}'

    def _param(self, node):
        return ':'.join([self._node(node[1]), self._node(node[2])])

    def _filters(self, node):
        ret = '"%s"' % self.auto
        f_list = ['"%s"' % f for f in node[1:]]  # repr?
        if f_list:
            ret += ',[%s]' % ','.join(f_list)
        return ret

    def _key(self, node):
        return 'ctx.get(%r)' % node[1]

    def _path(self, node):
        cur = node[1]
        keys = node[2] or []
        return 'ctx.get_path(%s, %s)' % (cur, keys)

    def _literal(self, node):
        return escape(node[1])


#########
# Runtime
#########
def escape_html(text):
    text = unicode(text)
    # TODO: dust.js doesn't use this, but maybe we should: .replace("'", '&squot;')
    return cgi.escape(text, True)


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


def sep_helper(chunk, context, bodies):
    if context.stack.index == context.stack.of - 1:
        return chunk
    return bodies.block(chunk, context)


def idx_helper(chunk, context, bodies):
    return bodies.block(chunk, context.push(context.stack.index))


DEFAULT_HELPERS = {'sep': sep_helper, 'idx': idx_helper}


class Context(object):
    def __init__(self, env, stack, global_vars=None, blocks=None):
        self.env = env
        self.stack = stack
        if global_vars is None:
            global_vars = {}
        self.globals = global_vars
        self.blocks = blocks

    @classmethod
    def wrap(cls, env, context):
        if isinstance(context, cls):
            return context
        return cls(env, Stack(context))

    def get(self, key):
        ctx = self.stack
        value = None
        while ctx:
            try:
                value = ctx.head[key]
            except (AttributeError, KeyError, TypeError):
                ctx = ctx.tail
            else:
                return value
        if value is None:
            return self.globals.get(key)
        else:
            return value

    def get_path(self, cur, down):
        ctx = self.stack
        length = len(down)  # TODO: try/except?
        if cur and not length:
            return ctx.head  # aka implicit
        try:
            ctx = ctx.head
        except AttributeError:
            return None
        for down_part in down:
            try:
                ctx = ctx[down_part]
            except (AttributeError, TypeError):
                break
            except KeyError:
                return None
        return ctx

    def push(self, head, index=None, length=None):
        return Context(self.env,
                       Stack(head, self.stack, index, length),
                       self.globals,
                       self.blocks)

    def rebase(self, head):
        return Context(self.env,
                       Stack(head),
                       self.globals,
                       self.blocks)

    def current(self):
        return self.stack.head

    def get_block(self, key):
        blocks = self.blocks
        if not blocks:
            return None
        fn = None
        for block in blocks[::-1]:
            try:
                fn = block[key]
                if fn:
                    break
            except KeyError:
                continue
        return fn

    def shift_blocks(self, local_vars):
        blocks = self.blocks
        if local_vars:
            if blocks:
                new_blocks = blocks + [local_vars]
            else:
                new_blocks = [local_vars]
            return Context(self.env, self.stack, self.globals, new_blocks)
        return self


class Stack(object):
    def __init__(self, head, tail=None, index=None, length=None):
        self.head = head
        self.tail = tail
        self.index = index or 0
        self.of = length or 1
        #self.is_object = is_scalar(head)

    def __repr__(self):
        return 'Stack(%r, %r, %r, %r)' % (self.head,
                                          self.tail,
                                          self.index,
                                          self.of)


class Stub(object):
    def __init__(self, callback):
        self.head = Chunk(self)
        self.callback = callback
        self.out = ''  # TODO: convert to list, use property and ''.join()

    def flush(self):
        chunk = self.head
        while chunk:
            if chunk.flushable:
                self.out += chunk.data
            elif chunk.error:
                self.callback(chunk.error, '')
                self.flush = lambda self: None
                return
            else:
                return
            self.head = chunk = chunk.next
        self.callback(None, self.out)


class Stream(object):
    def __init__(self):
        self.head = Chunk(self)
        self.events = {}

    def flush(self):
        chunk = self.head
        while chunk:
            if chunk.flushable:
                self.emit('data', chunk.data)
            elif chunk.error:
                self.emit('error', chunk.error)
                self.flush = lambda self: None
                return
            else:
                return
            self.head = chunk = chunk.next
        self.emit('end')

    def emit(self, etype, data=None):
        try:
            self.events[etype](data)
        except KeyError:
            pass

    def on(self, etype, callback):
        self.events[etype] = callback
        return self


def is_scalar(obj):
    return not hasattr(obj, '__iter__') or isinstance(obj, basestring)


def is_empty(obj):
    try:
        return obj is None or obj is False or len(obj) == 0
    except TypeError:
        return False


class Chunk(object):
    def __init__(self, root, next_chunk=None, taps=None):
        self.root = root
        self.next = next_chunk
        self.taps = taps
        self.data = ''
        self.flushable = False
        self.error = None

    def write(self, data):
        if self.taps:
            data = self.taps.go(data)
        self.data += data
        return self

    def end(self, data=None):
        if data:
            self.write(data)
        self.flushable = True
        self.root.flush()
        return self

    def map(self, callback):
        cursor = Chunk(self.root, self.next, self.taps)
        branch = Chunk(self.root, cursor, self.taps)
        self.next = branch
        self.flushable = True
        callback(branch)
        return cursor

    def tap(self, tap):
        if self.taps:
            self.taps = self.taps.push(tap)
        else:
            self.taps = Tap(tap)
        return self

    def untap(self):
        self.taps = self.taps.tail
        return self

    def render(self, body, context):
        return body(self, context)

    def reference(self, elem, context, auto, filters=None):
        if callable(elem):
            # this whole callable thing is a pretty big TODO
            elem = elem(self, context, None, {'auto': auto,
                                              'filters': filters})
            if isinstance(elem, Chunk):
                return elem
        if is_empty(elem):
            return self
        else:
            filtered = context.env.apply_filters(elem, auto, filters)
            return self.write(filtered)

    def section(self, elem, context, bodies, params=None):
        if callable(elem):
            elem = elem(self, context, bodies, params)
            if isinstance(elem, Chunk):
                return elem
        body = bodies.get('block')
        else_body = bodies.get('else')
        if params:
            context = context.push(params)
        if not elem and else_body and elem is not 0:
            # breaks with dust.js; dust.js doesn't render else blocks
            # on sections referencing empty lists.
            return else_body(self, context)

        if not body or elem is None:
            return self
        if is_scalar(elem) or hasattr(elem, 'keys'):  # haaack
            if elem is True:
                return body(self, context)
            else:
                return body(self, context.push(elem))
        else:
            chunk = self
            length = len(elem)
            for i, el in enumerate(elem):
                chunk = body(chunk, context.push(el, i, length))
            return chunk

    def exists(self, elem, context, bodies, params=None):
        if not is_empty(elem):
            if bodies.get('block'):
                return bodies['block'](self, context)
        elif bodies.get('else'):
            return bodies['else'](self, context)
        return self

    def notexists(self, elem, context, bodies, params=None):
        if is_empty(elem):
            if bodies.get('block'):
                return bodies['block'](self, context)
        elif bodies.get('else'):
            return bodies['else'](self, context)
        return self

    def block(self, elem, context, bodies, params=None):
        body = bodies.get('block')
        if elem:
            body = elem
        if body:
            body(self, context)
        return self

    def partial(self, elem, context, bodies=None):
        if callable(elem):
            cback = lambda name, chk: context.env.load_chunk(name, chk, context).end()
            return self.capture(elem, context, cback)
        return context.env.load_chunk(elem, self, context)

    def helper(self, name, context, bodies, params=None):
        return context.env.helpers[name](self, context, bodies)

    def capture(self, body, context, callback):
        def map_func(chunk):
            def stub_cb(err, out):
                if err:
                    chunk.set_error(err)
                else:
                    callback(out, chunk)
            stub = Stub(stub_cb)
            body(stub.head, context).end()
        return self.map(map_func)

    def set_error(self, error):
        self.error = error
        self.root.flush()
        return self


class Tap(object):
    def __init__(self, head=None, tail=None):
        self.head = head
        self.tail = tail

    def push(self, tap):
        return Tap(tap, self)

    def go(self, value):
        tap = self
        while tap:
            value = tap.head(value)  # TODO: type errors?
            tap = tap.tail
        return value


DEFAULT_FILTERS = {
    'h': escape_html,
    'j': escape_js,
    'u': escape_uri,
    'uc': escape_uri_component}


###########
# Interface
###########


class Template(object):
    def __init__(self,
                 name,
                 source,
                 source_file=None,
                 optimize=True,
                 keep_source=True,
                 env=None,
                 lazy=False):
        self.name = name
        self.source = source
        self.source_file = source_file
        self.optimized = optimize
        if env is None:
            env = default_env
        self.env = env

        if lazy:  # lazy is really only for testing
            self.render_func = None
            return
        self.render_func = self._get_render_func(optimize)
        if not keep_source:
            self.source = None

    def render(self, model, env=None):
        env = env or self.env
        rendered = []

        def tmp_cb(err, result):
            if err:
                print 'Error on template %r: %r' % (self.name, err)
                raise Exception(err)
            else:
                rendered.append(result)
                return result

        chunk = Stub(tmp_cb).head
        self.render_chunk(chunk, Context.wrap(env, model)).end()
        return rendered[0]

    def render_chunk(self, chunk, context):
        if not self.render_func:
            self.render_func = self._get_render_func(self.optimized)
        return self.render_func(chunk, context)

    def _get_tokens(self):
        if not self.source:
            return None
        return tokenize(self.source)

    def _get_ast(self, optimize=False, raw=False):
        if not self.source:
            return None
        dast = ParseTree.from_source(self.source).to_dust_ast()
        if raw:
            return dast
        return self.env.filter_ast(dast, optimize)

    def _get_comp_str(self, optimize=False):
        ast = self._get_ast(optimize)
        if not ast:
            return None
        return Compiler(self.env)._gen_python(ast)

    def _get_render_func(self, optimize=True):
        # switching over to optimize=True by default because it
        # makes the output easier to read and more like dust's docs
        ast = self._get_ast(optimize)
        if not ast:
            return None
        return Compiler(self.env).compile(ast)


class AshesEnv(object):
    def __init__(self,
                 filters=None,
                 helpers=None,
                 special_chars=None,
                 optimizers=None):
        self.templates = {}
        self.filters = dict(DEFAULT_FILTERS)
        if filters:
            self.filters.update(filters)
        self.helpers = dict(DEFAULT_HELPERS)
        if helpers:
            self.helpers.update(helpers)
        self.special_chars = dict(DEFAULT_SPECIAL_CHARS)
        if special_chars:
            self.special_chars.update(special_chars)
        self.optimizers = dict(DEFAULT_OPTIMIZERS)
        if optimizers:
            self.optimizers.update(optimizers)

    def register(self, template):
        try:
            if not template or not callable(template.render):
                raise AttributeError()
            self.templates[template.name] = template
        except AttributeError:
            raise ValueError('Invalid template: %r' % template)

    def render(self, name, model):
        try:
            template = self.templates[name]
        except KeyError:
            raise ValueError('No template named "%s"' % name)
        return template.render(model, self)

    def load(self, name):
        # TODO: this function (and raise better exceptions)
        return self.templates[name]

    def filter_ast(self, ast, optimize=True):
        if optimize:
            optimizers = self.optimizers
        else:
            optimizers = UNOPT_OPTIMIZERS
        optimizer = Optimizer(optimizers, self.special_chars)
        return optimizer.optimize(ast)

    def apply_filters(self, string, auto, filters):
        filters = filters or []
        if auto and 's' not in filters and auto not in filters:
            filters = filters + [auto]
        for f in filters:
            filt_fn = self.filters.get(f)
            if filt_fn:
                string = filt_fn(string)
        return string

    def load_chunk(self, name, chunk, context):
        try:
            tmpl = self.load(name)
        except KeyError:
            return chunk.set_error(Exception('Template not found "%s"' % name))
        return tmpl.render_chunk(chunk, context)


ashes = default_env = AshesEnv()
