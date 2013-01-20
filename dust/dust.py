# -*- coding: utf-8 -*-
"""
dust.py 0.4.0

Copyright (c) 2013 Mahmoud Hashemi
Copyright (c) 2012 Dan Nichols

Released under the MIT license.

dust.js 0.3.0

Copyright (c) 2010 Aleksander Williams

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import re
import urllib
import cgi
from cStringIO import StringIO


class Context(object):
    def __init__(self, attrs=None, parent=None, value=None):
        self.attrs = {}
        self.parent = parent
        self.value = value
        self.update(attrs)

    def get(self, name):
        if name in self.attrs:
            return self.attrs[name]
        elif self.parent:
            return self.parent.get(name)
        else:
            return None

    def set(self, name, value):
        self.attrs[name] = value

    def update(self, other):
        if not other:
            return

        if isinstance(other, dict):
            self.attrs.update(other)
        elif isinstance(other, Node):
            self.value = other
        elif type(other) in (str, list, tuple, set,
                             int, float, long, bool,
                             complex, unicode, bytearray,
                             buffer, xrange, frozenset):
            # ^ what the heck is this
            self.value = other
        elif isinstance(other, object):
            if hasattr(other, 'attrs'):
                self.attrs.update(other.attrs)
            else:
                self.attrs.update(other.__dict__)


class ContextResolver(object):
    # TODO: this needs a rework pretty bad. too many hasattr hazards in the mix
    def __init__(self, path):
        self.path = []
        if path.startswith('.'):
            self.path += ['.']
            self.path += path[1:].split('.')
        else:
            self.path = path.split('.')

    def __str__(self):
        path = []
        path.extend(self.path)
        if path[0] == '.':
            path[0] = ''
        return str('.'.join(path))

    def resolve(self, context, model):
        copy = Context(attrs=model, parent=context)
        if model:
            if isinstance(model, list):
                copy = []
                copy.extend(model)
            else:
                for segment in self.path:
                    if segment:
                        if segment == '.':
                            if copy.value:
                                copy = copy.value
                                break
                            else:
                                copy.parent = None
                        elif hasattr(copy, 'get') and copy.get(segment):
                            print copy
                            attrs = copy.get(segment)
                            copy = Context(attrs=attrs, parent=copy)
                        elif hasattr(copy, 'value'):
                            copy = copy.value
                        else:
                            break
                    else:
                        copy = copy.value
                        break
        else:
            copy = None
        return copy


class RenderChain(object):
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def get_block(self, name):
        block = self.tail.get_block(name)
        if block:
            return block
        elif self.head:
            return self.head.get_block(name)
        else:
            return None

    def __str__(self):
        return '[[%s] [%s]]' % (self.tail, str(self.head))


class Node(object):
    def __init__(self, blocks=None):
        self.blocks = blocks if blocks else {}

    def render(self, chain, context, model, env=None):
        raise Exception('Abstract')

    def __str__(self):
        return '<Node>'

    def get_block(self, name):
        if self.has_block(name):
            return self.blocks[name].as_block()
        else:
            return None

    def set_block(self, name, value):
        self.blocks[name] = value

    def has_block(self, name):
        return name in self.blocks

    def as_block(self):
        return self


class NodeList(Node):
    def __init__(self, blocks=None, nodes=None):
        super(NodeList, self).__init__(blocks=blocks)
        self.nodes = []
        if nodes:
            self.nodes.extend(nodes)

    def __iter__(self):
        return iter(self.nodes)

    def add(self, node):
        self.nodes.append(node)
        return node

    def last(self):
        count = len(self.nodes)
        if count > 0:
            return self.nodes[count - 1]
        else:
            return None

    def prepare_model(self, chain, context, model):
        return Context(attrs=model, parent=context)

    def render(self, chain, context, model, env=None):
        chain = RenderChain(chain, self)
        model = self.prepare_model(chain, context, model)
        sb = StringIO()
        if model is not None:
            for node in self.nodes:
                sb.write(node.render(chain, context, model, env=env))
        out = sb.getvalue()
        sb.close()
        return out

    def __str__(self):
        return ''.join([str(n) for n in self.nodes])


class TextNode(Node):
    def __init__(self, blocks=None, value=''):
        super(TextNode, self).__init__(blocks=blocks)
        self.buffer = []
        self.buffer.append(value)
        self.value = value

    def write(self, value):
        if self.buffer is None:
            raise Exception('TextNode buffer is closed')
        self.buffer.append(value)

    def close(self):
        if self.buffer:
            self.value = ''.join(self.buffer)
            self.buffer = None

    def render(self, chain, context, model, env=None):
        return str(self)

    def __str__(self):
        self.close()
        return self.value


class VariableNode(Node):
    def __init__(self, path, blocks=None, filters=None):
        super(VariableNode, self).__init__(blocks=blocks)
        self.context = ContextResolver(path)
        self.filters = []
        if filters:
            self.filters.extend(filters)

    def __str__(self):
        if self.filters:
            return '{%s|%s}' % (self.context, '|'.join(self.filters))
        else:
            return '{%s}' % self.context

    def render(self, chain, context, model, env=None):
        if env is None:
            env = default_env
        chain = RenderChain(chain, self)
        orig_model = model
        model = self.context.resolve(context, model)
        result = ''
        if model is not None:
            if isinstance(model, Node):
                result = model.render(chain, context, orig_model, env=env)
            elif isinstance(model, ContextResolver):
                result = model.resolve(context, orig_model)
            elif isinstance(model, Context):
                result = model.value
            else:
                result = str(model)
            if self.filters:
                for flag in self.filters:
                    if flag in env.filters:
                        env.filters[flag](result)
            else:
                result = escape_html(result)
        return result


class LogicNode(Node):
    operator = '#'
    allow_iter = True

    def __init__(self, path, scope, params, blocks=None, bodies=None):
        super(LogicNode, self).__init__(blocks=blocks)
        self.bodies = {}
        if bodies:
            self.bodies.update(bodies)
        else:
            self.start_body('block')
        self.params = {}
        if params:
            self.params.update(params)
        self.context = ContextResolver(path) if path else None
        self.scope = ContextResolver(scope) if scope else None

    def __str__(self):
        result = '{%s%s' % (self.operator, str(self.context))
        if self.scope:
            result += ':%s' % str(self.scope)
        for name in self.params:
            result += ' %s=' % name
            value = self.params[name]
            if isinstance(value, NodeList):
                result += '"'
                for node in value:
                    result += str(node)
                result += '"'
            elif isinstance(value, VariableNode):
                result += str(value.context)
            elif isinstance(value, TextNode):
                result += '"%s"' % str(value)
            else:
                result += str(value)
        result += '}%s' % str(self.bodies['block'])
        for name in self.bodies:
            if name != 'block':
                result += '{:%s}%s' % (name, str(self.bodies[name]))
        result += '{/%s}' % str(self.context)
        return result

    def start_body(self, name):
        body = NodeList()
        self.current_body = self.bodies[name] = body
        return body

    def end_body(self):
        self.current_body = None

    def prepare_model(self, chain, context, model):
        result = Context(attrs=model, parent=context)
        for param, node in self.params.iteritems():
            # BIG TODO: does prepare_model need env=env, too?
            result.set(param, node.render(chain, context, context))
        result.update(model)
        return result

    def render_body(self, name, chain, context, model, env=None):
        sb = StringIO()
        body = self.bodies.get(name)
        context = model
        if self.scope:
            model = self.scope.resolve(context, model)
        elif self.context:
            model = self.context.resolve(context, model)
        if body:
            chain = RenderChain(chain, body)
            if self.allow_iter and isinstance(model, list):
                length = len(model)
                for i in range(length):
                    iter_model = self.prepare_model(chain, context, model[i])
                    iter_model.update({
                        '@idx': i,
                        '@sep': i != length - 1})
                    sb.write(body.render(chain, context, iter_model, env=env))
            else:
                iter_model = self.prepare_model(chain, context, model)
                sb.write(body.render(chain, context, iter_model, env=env))
        out = sb.getvalue()
        sb.close()
        return out

    def choose_body_name(self, context, model):
        return 'block' if self.context.resolve(context, model) else 'else'

    def render(self, chain, context, model, env=None):
        chain = RenderChain(chain, self)
        context = Context(attrs=self.params, parent=context)
        body_name = self.choose_body_name(context, model)
        return self.render_body(body_name, chain, context, model, env=env)


class ExistsNode(LogicNode):
    operator = '?'
    allow_iter = False

    def prepare_model(self, chain, context, model):
        result = Context(attrs=context, parent=context)
        result.update(self.params)
        return result


class NotExistsNode(ExistsNode):
    operator = '^'

    def choose_body_name(self, context, model):
        return 'else' if self.context.resolve(context, model) else 'block'


class HelperNode(LogicNode):
    allow_iter = False

    def __init__(self, name, scope, params, blocks=None, bodies=None):
        super(HelperNode, self).__init__(None, scope, params, blocks=blocks,
                                         bodies=bodies)
        self.context = name

    def render(self, chain, context, model, env=None):
        if env is None:
            env = default_env
        chain = RenderChain(chain, self)
        context = Context(attrs=self.params, parent=context)
        helper = env.helpers[self.context]
        return helper(chain, context, model)


class IndexNode(NodeList):
    def prepare_model(self, chain, context, model):
        if model.get('@idx') is not None:
            return str(model.get('@idx'))
        else:
            return None

    def __str__(self):
        return '{@idx}%s{/idx}' % super(IndexNode, self).__str__()


class SepNode(NodeList):
    def prepare_model(self, chain, context, model):
        if model.get('@sep'):
            return super(SepNode, self).prepare_model(chain, context, model)
        else:
            return None

    def __str__(self):
        return '{@sep}%s{/sep}' % super(SepNode, self).__str__()


class EscapedCharacterNode(Node):
    characters = {
        'n': '\n',
        'r': '\r',
        's': ' ',
        'lb': '{',
        'rb': '}'
    }

    def __init__(self, code, blocks=None):
        super(EscapedCharacterNode, self).__init__(blocks=blocks)
        self.code = code
        self.character = self.characters[code]

    def __str__(self):
        return '{~%s}' % self.code

    def render(self, chain, context, model, env=None):
        return self.character


class PartialNode(Node):
    def __init__(self, include, scope, blocks=None):
        super(PartialNode, self).__init__(blocks=blocks)
        self.include = include
        self.scope = ContextResolver(scope) if scope else None

    def __str__(self):
        result = '{>%s' % self.include
        if self.scope:
            result += ':%s' % str(self.scope)
        return '%s/}' % result

    def render(self, chain, context, model, env=None):
        if env is None:
            env = default_env
        if self.scope:
            model = self.scope.resolve(context, model)
        chain = RenderChain(chain, self)
        name = self.include
        if isinstance(self.include, NodeList):
            name = self.include.render(chain, context, model, env=env)
        template = env.load(name)
        return template.render(chain, context, model, env=env)


class BlockNode(NodeList):
    def __init__(self, name, blocks=None, nodes=None):
        super(BlockNode, self).__init__(blocks=blocks, nodes=nodes)
        self.name = name

    def __str__(self):
        return '{+%s}%s{/%s}' % (self.name, super(BlockNode, self), self.name)

    def render(self, chain, context, model, env=None):
        if env is None:
            env = dust
        block = chain.get_block(self.name)
        if block:
            return block.render(chain, context, model, env=env)
        else:
            return super(BlockNode, self).render(chain, context, model,
                                                 env=env)


class InlinePartialNode(NodeList):
    def __init__(self, name, blocks=None, nodes=None):
        super(InlinePartialNode, self).__init__(blocks=blocks, nodes=nodes)
        self.name = name

    def __str__(self):
        super_node = super(InlinePartialNode, self)
        return '{<%s}%s{/%s}' % (self.name, super_node, self.name)

    def as_block(self):
        result = NodeList()
        result.nodes.extend(self.nodes)
        return result

    def render(self, chain, context, model, env=None):
        return ''


class NodeListParser(object):
    def __init__(self):
        self.last_end = 0

    def parse(self, string, env=None):
        if env is None:
            env = default_env
        # removing comments
        string = re.sub(r'\{!.+?!\}', '', string, flags=re.DOTALL).strip()
        nodes = [NodeList()]
        depth = 0
        exp = re.compile(
            r'(\{[\~\#\?\@\:\<\>\+\/\^]?([a-zA-Z0-9_\$\.]+|"[^"]+")(\:[a-'
            r'zA-Z0-9\$\.]+)?(\|[a-z]+)*?( \w+\=(("[^"]*?")|([\w\.]+)))*?'
            r'\/?\})', flags=re.MULTILINE)
        last_end = 0
        start = None
        end = None
        for match in re.finditer(exp, string):
            depth_change = False
            start = match.start(1)
            end = match.end(1)
            if last_end != start:
                head = string[last_end:start]
                if head:
                    nodes[depth].add(TextNode(value=head))
            last_end = end
            node = None
            tag = string[start + 1:end - 1]
            operator = tag[0]
            tag = tag.split(' ')
            if operator in ['~', '#', '?', '@', ':', '<', '>', '+', '/', '^']:
                tag_name = tag[0][1:].split(':')
                scope = tag_name[1] if len(tag_name) > 1 else None
                tag_name = tag_name[0]
                params = None
                self_closed = tag_name.endswith('/')
                if self_closed:
                    tag_name = tag_name[:-1]
                elif scope and scope.endswith('/'):
                    scope = scope[:-1]
                    self_closed = True
                if operator == '~':
                    node = EscapedCharacterNode(tag_name)
                elif operator == '#':
                    if tag_name in env.helpers:
                        node = HelperNode(tag_name, scope, params)
                    else:
                        node = LogicNode(tag_name, scope, params)
                elif operator == '?':
                    node = ExistsNode(tag_name, scope, params)
                elif operator == '^':
                    node = NotExistsNode(tag_name, scope, params)
                elif operator == '@':
                    name = tag[0][1:]
                    if name == 'idx':
                        node = IndexNode()
                    elif name == 'sep':
                        node = SepNode()
                elif operator == '>':
                    is_external = tag_name.startswith('"')
                    if is_external:
                        tag_name = self.parse(tag_name.strip('"'))
                    node = PartialNode(tag_name, scope)
                elif operator == '+':
                    node = BlockNode(tag_name)
                elif operator == '<':
                    node = InlinePartialNode(tag_name)
                else:
                    node = TextNode(value='UNDEFINED:' + ' '.join(tag))
                if not self_closed:
                    if operator in ['#', '?', '^', '@', ':', '+', '<']:
                        depth_change = True
                        for param in tag[1:]:
                            param = param.split('=')
                            name = param[0]
                            value = '='.join(param[1:])
                            if not value.startswith('"'):
                                value = VariableNode(value)
                            else:
                                value = self.parse(value.strip('"'))
                            node.params[name] = value
                        if isinstance(node, NodeList):
                            if isinstance(node, InlinePartialNode):
                                nodes[depth].set_block(node.name, node)
                            nodes[depth].add(node)
                            depth += 1
                            nodes.insert(depth, node)
                        elif isinstance(node, LogicNode):
                            nodes[depth].add(node)
                            depth += 1
                            nodes.insert(depth, node.current_body)
                        else:
                            root = nodes[depth - 1].last()
                            root.end_body()
                            nodes[depth] = root.start_body(tag_name)
                    elif operator in '/':
                        depth_change = True
                        if depth > 0:
                            nodes.pop(depth)
                            depth -= 1
            else:
                tag = tag[0].split('|')
                filters = tag[1:]
                tag = tag[0]
                node = VariableNode(tag, filters=filters)
            if node and not depth_change:
                nodes[depth].add(node)
        tail = string[last_end:]
        if tail:
            nodes[depth].add(TextNode(value=tail))
        return nodes[0]


class Template(object):
    def __init__(self, name, root_node, src_file=None):
        self.name = name
        self.root_node = root_node
        self.src_file = src_file

    def render(self, model, chain=None, context=None, env=None):
        return self.root_node.render(chain, context, model, env=env)


def escape_html(text):
    text = str(text)
    return cgi.escape(text, True).replace("'", '&squot;')


def escape_js(text):
    text = str(text)
    return (string
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


class DustEnv(object):
    default_filters = {
        'h': escape_html,
        'j': escape_js,
        'u': escape_uri,
        'uc': escape_uri_component}

    def __init__(self):
        self.parser = NodeListParser()
        self.templates = {}
        self.helpers = {}
        self.filters = dict(self.default_filters)

    def compile(self, string, name, src_file=None):
        root_node = self.parser.parse(string)
        self.templates[name] = Template(name, root_node, src_file=src_file)
        return root_node

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


dust = default_env = DustEnv()
