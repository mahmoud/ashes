from __future__ import unicode_literals

from .core import AshesTest

heading = 'Dust.js site refs'

class Plain(AshesTest):
    template = 'Hello World!'
    json_ast = '["body", ["buffer", "Hello World!"]]'
    json_context = '{}'
    rendered = 'Hello World!'


class Path(AshesTest):
    template = '{foo.bar}'
    json_ast = '["body", ["reference", ["path", false, ["foo", "bar"]], ["filters"]]]'
    json_context = '{"foo": {"bar": "Hello!"}}'
    rendered = 'Hello!'


def sync_chunk_func(chunk, *a, **kw):
    return chunk.write('Chunky')


class SyncChunk(AshesTest):
    template = 'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    rendered = 'Hello Chunky World!'
    context = {'type': sync_chunk_func}


class Zero(AshesTest):
    template = '{#zero}{.}{/zero}'
    json_ast = '["body", ["#", ["key", "zero"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]]]'
    json_context = '{"zero": 0}'
    rendered = '0'


class PartialContext(AshesTest):
    template = '{>replace:.profile/}'
    json_ast = '["body", ["partial", ["literal", "replace"], ["context", ["path", true, ["profile"]]], ["params"]]]'
    json_context = '{"profile": {"count": 30, "name": "Mick"}}'
    rendered = 'Hello Mick! You have 30 new messages.'


class SyncKey(AshesTest):
    template = 'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    json_context = '{\n  "type": function(chunk) {\n    return "Sync";\n  }\n}'
    rendered = 'Hello Sync World!'
    context = {'type': lambda *a, **kw: 'Sync'}


class Comments(AshesTest):
    template = '{!\n  Multiline\n  {#foo}{bar}{/foo}\n!}\n{!before!}Hello{!after!}'
    json_ast = '["body", ["comment", "\\n  Multiline\\n  {#foo}{bar}{/foo}\\n"], ["format", "\\n", ""], ["comment", "before"], ["buffer", "Hello"], ["comment", "after"]]'
    json_context = '{}'
    rendered = 'Hello'


def params_helper(chunk, context, bodies, params):
    return chunk.write(params.get('foo'))

class Params(AshesTest):
    template = '{#helper foo="bar"/}'
    json_ast = '["body", ["#", ["key", "helper"], ["context"], ["params", ["param", ["literal", "foo"], ["literal", "bar"]]], ["bodies"]]]'
    json_context = '{\n  "helper": function(chunk, context, bodies, params) {\n    return chunk.write(params.foo);\n  }\n}'
    context = {'helper': params_helper}
    rendered = 'bar'


class Implicit(AshesTest):
    template = '{#names}{.}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": ["Moe", "Larry", "Curly"]}'
    rendered = 'Moe\nLarry\nCurly'


class Replace(AshesTest):
    template = 'Hello {name}! You have {count} new messages.'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "name"], ["filters"]], ["buffer", "! You have "], ["reference", ["key", "count"], ["filters"]], ["buffer", " new messages."]]'
    json_context = '{"count": 30, "name": "Mick"}'
    rendered = 'Hello Mick! You have 30 new messages.'


def async_key_func(chunk, *a, **kw):
    return chunk.map(lambda chk: chk.end('Async'))


class AsyncKey(AshesTest):
    template = 'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    json_context = '{\n  "type": function(chunk) {\n    return chunk.map(function(chunk) {\n      dust.nextTick(function() {\n        chunk.end("Async");\n      });\n    });\n  }\n}'
    rendered = 'Hello Async World!'
    context = {'type': async_key_func}


class EmptyArray(AshesTest):
    template = '{#names}{title} {name}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "title"], ["filters"]], ["buffer", " "], ["reference", ["key", "name"], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": [], "title": "Sir"}'
    rendered = ''


class Escaped(AshesTest):
    template = '{safe|s}{~n}{unsafe}'
    json_ast = '["body", ["reference", ["key", "safe"], ["filters", "s"]], ["special", "n"], ["reference", ["key", "unsafe"], ["filters"]]]'
    json_context = '{"safe": "<script>alert(\'Hello!\')</script>", "unsafe": "<script>alert(\'Goodbye!\')</script>"}'
    rendered = "<script>alert('Hello!')</script>\n&lt;script&gt;alert(&#x27;Goodbye!&#x27;)&lt;/script&gt;"


class Partials(AshesTest):
    template = '{>replace/} {>"plain"/} {>"{ref}"/} {>"p{ref2}n"/}'
    json_ast = '["body", ["partial", ["literal", "replace"], ["context"], ["params"]], ["buffer", " "], ["partial", ["literal", "plain"], ["context"], ["params"]], ["buffer", " "], ["partial", ["body", ["reference", ["key", "ref"], ["filters"]]], ["context"], ["params"]], ["buffer", " "], ["partial", ["body", ["buffer", "p"], ["reference", ["key", "ref2"], ["filters"]], ["buffer", "n"]], ["context"], ["params"]]]'
    json_context = '{"count": 42, "ref": "plain", "ref2": "lai", "name": "Jim"}'
    rendered = 'Hello Jim! You have 42 new messages. Hello World! Hello World! Hello World!'


class Recursion(AshesTest):
    template = '{name}{~n}{#kids}{>recursion:./}{/kids}'
    json_ast = '["body", ["reference", ["key", "name"], ["filters"]], ["special", "n"], ["#", ["key", "kids"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["partial", ["literal", "recursion"], ["context", ["path", true, []]], ["params"]]]]]]]'
    json_context = '{"kids": [{"kids": [{"name": "1.1.1"}], "name": "1.1"}], "name": "1"}'
    rendered = '1\n1.1\n1.1.1'


class Array(AshesTest):
    template = '{#names}{title} {name}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "title"], ["filters"]], ["buffer", " "], ["reference", ["key", "name"], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": [{"name": "Moe"}, {"name": "Larry"}, {"name": "Curly"}], "title": "Sir"}'
    rendered = 'Sir Moe\nSir Larry\nSir Curly'


class Object(AshesTest):
    template = '{#person}{root}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "root"], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = 'Subject: Larry, 45'


def filter_func(chunk, context, bodies, *a, **kw):
    return (chunk.tap(lambda data: data.upper())
            .render(bodies['block'], context)
            .untap())


class Filter(AshesTest):
    template = '{#filter}foo {bar}{/filter}'
    json_ast = '["body", ["#", ["key", "filter"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "foo "], ["reference", ["key", "bar"], ["filters"]]]]]]]'
    json_context = '{\n  "filter": function(chunk, context, bodies) {\n    return chunk.tap(function(data) {\n      return data.toUpperCase();\n    }).render(bodies.block, context).untap();\n  },\n  "bar": "bar"\n}'
    rendered = 'FOO BAR'
    context = {'filter': filter_func,
               'bar': 'bar'}


class ForceCurrent(AshesTest):
    template = '{#person}{.root}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, ["root"]], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = ': Larry, 45'


class RenameKey(AshesTest):
    template = '{#person foo=root}{foo}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params", ["param", ["literal", "foo"], ["key", "root"]]], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "foo"], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = 'Subject: Larry, 45'


class InterpolatedParam(AshesTest):
    template = '{#person foo="{root}_id"}{foo}: {name}, {age}{/person}'
    json_ast = '''["body",["#",["key","person"],["context"],["params",["param",["literal","foo"],["body",["reference",["key","root"],["filters"]],["buffer","_id"]]]],["bodies",["param",["literal","block"],["body",["reference",["key","foo"],["filters"]],["buffer",": "],["reference",["key","name"],["filters"]],["buffer",", "],["reference",["key","age"],["filters"]]]]]]]'''
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = 'Subject_id: Larry, 45'


class EscapePragma(AshesTest):
    template = '{%esc:s}\n  {unsafe}{~n}\n  {%esc:h}\n    {unsafe}\n  {/esc}\n{/esc}'
    json_ast = r'["body",["%",["key","esc"],["context",["key","s"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["reference",["key","unsafe"],["filters"]],["special","n"],["format","\n","  "],["%",["key","esc"],["context",["key","h"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","    "],["reference",["key","unsafe"],["filters"]],["format","\n","  "]]]]],["format","\n",""]]]]]]'
    json_opt_ast = r'["body",["%",["key","esc"],["context",["key","s"]],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","unsafe"],["filters"]],["buffer","\n"],["%",["key","esc"],["context",["key","h"]],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","unsafe"],["filters"]]]]]]]]]]]'
    json_context = '{"unsafe": "<script>alert(\'Goodbye!\')</script>"}'
    rendered = '''<script>alert('Goodbye!')</script>\n&lt;script&gt;alert(&#x27;Goodbye!&#x27;)&lt;/script&gt;'''


class Intro(AshesTest):
    template = '{#stream}{#delay}{.}{/delay}{/stream}'
    json_ast = '["body", ["#", ["key", "stream"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["#", ["key", "delay"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]]]]]]]'
    #json_context = 'function() {\n  var d = 1;\n  return {\n    stream: function() {\n      return "asynchronous templates for the browser and node.js".split(\'\');\n    },\n    delay: function(chunk, context, bodies) {\n      return chunk.map(function(chunk) {\n        setTimeout(function() {\n          chunk.render(bodies.block, context).end();\n        }, d++ * 15);\n      });\n    }\n  }\n}'
    rendered = ''


class BaseTemplate(AshesTest):
    template = 'Start{~n}\n{+title}\n  Base Title\n{/title}\n{~n}\n{+main}\n  Base Content\n{/main}\n{~n}\nEnd'
    json_ast = '["body", ["buffer", "Start"], ["special", "n"], ["format", "\\n", ""], ["+", ["key", "title"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Base Title"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["+", ["key", "main"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Base Content"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["buffer", "End"]]'
    json_context = '{}'
    rendered = 'Start\nBase Title\nBase Content\nEnd'


def async_iter_func(chunk, context, bodies, params):
    return chunk.map(lambda chk: chk.render(bodies['block'], context).end())


class AsyncIterator(AshesTest):
    template = '{#numbers}{#delay}{.}{/delay}{@sep}, {/sep}{/numbers}'
    json_ast = '["body", ["#", ["key", "numbers"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["#", ["key", "delay"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]], ["@", ["key", "sep"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", ", "]]]]]]]]]]'
    json_context = '{\n  "numbers": [\n  3, 2, 1],\n  "delay": function(chunk, context, bodies) {\n    return chunk.map(function(chunk) {\n      setTimeout(function() {\n        chunk.render(bodies.block, context).end();\n      }, Math.ceil(Math.random() * 10));\n    });\n  }\n}'
    rendered = '3, 2, 1'
    context = {'numbers': [3, 2, 1],
               'delay': async_iter_func}


class ElseBlock(AshesTest):
    template = '{#foo}\n  foo,{~s}\n{:else}\n  not foo,{~s}\n{/foo}\n{#bar}\n  bar!\n{:else}\n  not bar!\n{/bar}'
    json_ast = '["body", ["#", ["key", "foo"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "not foo,"], ["special", "s"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "foo,"], ["special", "s"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["#", ["key", "bar"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "not bar!"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "bar!"], ["format", "\\n", ""]]]]]]'
    json_context = '{"foo": true, "bar": false}'
    rendered = 'foo, not bar!'


def context_func(chunk, context, bodies, *a, **kw):
    items = context.current()
    if items:
        chunk.write('<ul>\n')
        for i in items:
            (chunk.write('<li>')
             .render(bodies['block'], context.push(i))
             .write('</li>\n'))
        return chunk.write('</ul>')
    elif 'else' in bodies:
        return chunk.render(bodies['else'], context)
    return chunk


class Context(AshesTest):
    template = '{#list:projects}{name}{:else}No Projects!{/list}'
    json_ast = '["body", ["#", ["key", "list"], ["context", ["key", "projects"]], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "No Projects!"]]], ["param", ["literal", "block"], ["body", ["reference", ["key", "name"], ["filters"]]]]]]]'
    json_context = '{\n  "list": function(chunk, context, bodies) {\n    var items = context.current(),\n        len = items.length;\n\n    if (len) {\n      chunk.write("<ul>\\n");\n      for (var i = 0; i < len; i++) {\n        chunk = chunk.write("<li>").render(bodies.block, context.push(items[i])).write("</li>\\n");\n      }\n      return chunk.write("</ul>");\n    } else if (bodies[\'else\']) {\n      return chunk.render(bodies[\'else\'], context);\n    }\n    return chunk;\n  },\n  "projects": [{\n    "name": "Mayhem"\n  },\n  {\n    "name": "Flash"\n  },\n  {\n    "name": "Thunder"\n  }]\n}'
    rendered = '<ul>\n<li>Mayhem</li>\n<li>Flash</li>\n<li>Thunder</li>\n</ul>'
    context = {'list': context_func,
               'projects': [{'name': 'Mayhem'},
                            {'name': 'Flash'},
                            {'name': 'Thunder'}]}


class ChildTemplate(AshesTest):
    template = '{^xhr}\n  {>base_template/}\n{:else}\n  {+main/}\n{/xhr}\n{<title}\n  Child Title\n{/title}\n{<main}\n  Child Content\n{/main}\n'
    json_ast = '["body", ["^", ["key", "xhr"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["+", ["key", "main"], ["context"], ["params"], ["bodies"]], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["partial", ["literal", "base_template"], ["context"], ["params"]], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["<", ["key", "title"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Child Title"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["<", ["key", "main"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Child Content"], ["format", "\\n", ""]]]]], ["format", "\\n", ""]]'
    json_context = '{"xhr": false}'
    rendered = 'Start\nChild Title\nChild Content\nEnd'


class Conditional(AshesTest):
    template = '{?tags}\n  <ul>{~n}\n    {#tags}\n      {~s} <li>{.}</li>{~n}\n    {/tags}\n  </ul>\n{:else}\n  No Tags!\n{/tags}\n{~n}\n{^likes}\n  No Likes!\n{:else}\n  <ul>{~n}\n    {#likes}\n      {~s} <li>{.}</li>{~n}\n    {/likes}\n  </ul>\n{/likes}'
    json_ast = '["body", ["?", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "No Tags!"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "<ul>"], ["special", "n"], ["format", "\\n", "    "], ["#", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "      "], ["special", "s"], ["buffer", " <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>"], ["special", "n"], ["format", "\\n", "    "]]]]], ["format", "\\n", "  "], ["buffer", "</ul>"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["^", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "<ul>"], ["special", "n"], ["format", "\\n", "    "], ["#", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "      "], ["special", "s"], ["buffer", " <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>"], ["special", "n"], ["format", "\\n", "    "]]]]], ["format", "\\n", "  "], ["buffer", "</ul>"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "No Likes!"], ["format", "\\n", ""]]]]]]'
    json_opt_ast = '["body", ["?", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "No Tags!"]]], ["param", ["literal", "block"], ["body", ["buffer", "<ul>\\n"], ["#", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "  <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>\\n"]]]]], ["buffer", "</ul>"]]]]], ["buffer", "\\n"], ["^", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "<ul>\\n"], ["#", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "  <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>\\n"]]]]], ["buffer", "</ul>"]]], ["param", ["literal", "block"], ["body", ["buffer", "No Likes!"]]]]]]'
    json_context = '{"likes": ["moe", "larry", "curly", "shemp"], "tags": []}'
    rendered = 'No Tags!\n<ul>\n  <li>moe</li>\n  <li>larry</li>\n  <li>curly</li>\n  <li>shemp</li>\n</ul>'
