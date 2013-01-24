from __future__ import unicode_literals

import re
import cgi
import json
import urllib


parse_tests = {
    'plain': 'Hello World!',
    'replace': 'Hello {name}! You have {count} new messages.',
    'array': '{#names}{title} {name}{~n}{/names}',
    'implicit': '{#names}{.}{~n}{/names}'}

parse_ref_json = {
    'plain': '["body",["buffer","Hello World!"]]',
    'replace': '''["body",["buffer","Hello "],["reference",["key","name"],
                  ["filters"]],["buffer","! You have "],["reference",
                  ["key","count"],["filters"]],["buffer"," new messages."]]''',
    'array': '''["body",["#",["key","names"],["context"],["params"],
                ["bodies",["param",["literal","block"],["body",
                ["reference",["key","title"],["filters"]],
                ["buffer"," "],["reference",["key","name"],
                ["filters"]],["special","n"]]]]]]''',
    'implicit': '''["body",["#",["key","names"],["context"],["params"],
                   ["bodies",["param",["literal","block"],
                   ["body",["reference",["path",true,[]],
                   ["filters"]],["special","n"]]]]]]'''
    }

parse_ref = dict([(k, json.loads(v)) for k, v
                      in parse_ref_json.items()])


# don't ask, because who even knows, okay?
node_re = re.compile(r'(\{[\~\#\?\@\:\<\>\+\/\^]?'
                     r'([a-zA-Z0-9_\$\.]+|"[^"]+")'
                     r'(\:[a-zA-Z0-9\$\.]+)?(\|[a-z]+)*?'
                     r'( \w+\=(("[^"]*?")|([\w\.]+)))*?\/?\})',
                     flags=re.MULTILINE)


#comment_re = ''  # TODO
def strip_comments(text):
    return re.sub(r'\{!.+?!\}', '', text, flags=re.DOTALL).strip()


def parse(source):
    # removing comments
    source = strip_comments(source)
    nodes = ['body']
    depth = 0
    last_end = 0
    start = None
    end = None
    for match in node_re.finditer(source):
        depth_change = False
        start, end = match.start(1), match.end(1)
        if last_end != start:
            head = source[last_end:start]
            if head:
                nodes.append(['buffer', head])
        last_end = end
        node = None
        tag = source[start + 1:end - 1]
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
                    tag_name = parse(tag_name.strip('"'))
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
                            value = parse(value.strip('"'))
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
    tail = source[last_end:]
    if tail:
        nodes.append(['buffer', tail])
    return nodes


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

def main():
    from pprint import pprint
    '''
    for k, v in parse_ref.items():
    print
    print k
    pprint(v)'''
    pprint(parse_ref['plain'])
    pprint(parse(parse_tests['plain']))
    return


if __name__ == '__main__':
    main()
