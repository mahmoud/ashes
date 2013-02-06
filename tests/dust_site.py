from __future__ import unicode_literals

from core import AshesTest


class Plain(AshesTest):
    template = u'Hello World!'
    json_ast = '["body", ["buffer", "Hello World!"]]'
    json_context = '{}'
    rendered = u'Hello World!'


class Path(AshesTest):
    template = u'{foo.bar}'
    json_ast = '["body", ["reference", ["path", false, ["foo", "bar"]], ["filters"]]]'
    json_context = '{"foo": {"bar": "Hello!"}}'
    rendered = u'Hello!'


def sync_chunk_func(chunk, *a, **kw):
    return chunk.write('Chunky')


class SyncChunk(AshesTest):
    template = u'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    rendered = u'Hello Chunky World!'
    context = {'type': sync_chunk_func}


class Zero(AshesTest):
    template = u'{#zero}{.}{/zero}'
    json_ast = '["body", ["#", ["key", "zero"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]]]'
    json_context = '{"zero": 0}'
    rendered = u'0'


class PartialContext(AshesTest):
    template = u'{>replace:.profile/}'
    json_ast = '["body", ["partial", ["literal", "replace"], ["context", ["path", true, ["profile"]]]]]'
    json_context = '{"profile": {"count": 30, "name": "Mick"}}'
    rendered = u'Hello Mick! You have 30 new messages.'


class SyncKey(AshesTest):
    template = u'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    json_context = u'{\n  "type": function(chunk) {\n    return "Sync";\n  }\n}'
    rendered = u'Hello Sync World!'
    context = {'type': lambda *a, **kw: 'Sync'}


class Comments(AshesTest):
    template = u'{!\n  Multiline\n  {#foo}{bar}{/foo}\n!}\n{!before!}Hello{!after!}'
    #json_ast = '["body", ["comment", "\\n  Multiline\\n  {#foo}{bar}{/foo}\\n"], ["format", "\\n", ""], ["comment", "before"], ["buffer", "Hello"], ["comment", "after"]]'
    json_context = '{}'
    rendered = u'Hello'


def params_helper(chunk, context, bodies, params):
    return chunk.write(params.get('foo'))

class Params(AshesTest):
    template = u'{#helper foo="bar"/}'
    json_ast = '["body", ["#", ["key", "helper"], ["context"], ["params", ["param", ["literal", "foo"], ["literal", "bar"]]], ["bodies"]]]'
    json_context = u'{\n  "helper": function(chunk, context, bodies, params) {\n    return chunk.write(params.foo);\n  }\n}'
    context = {'helper': params_helper}
    rendered = u'bar'


class Implicit(AshesTest):
    template = u'{#names}{.}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": ["Moe", "Larry", "Curly"]}'
    rendered = u'Moe\nLarry\nCurly'


class Replace(AshesTest):
    template = u'Hello {name}! You have {count} new messages.'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "name"], ["filters"]], ["buffer", "! You have "], ["reference", ["key", "count"], ["filters"]], ["buffer", " new messages."]]'
    json_context = '{"count": 30, "name": "Mick"}'
    rendered = u'Hello Mick! You have 30 new messages.'


def async_key_func(chunk, *a, **kw):
    return chunk.map(lambda chk: chk.end('Async'))


class AsyncKey(AshesTest):
    template = u'Hello {type} World!'
    json_ast = '["body", ["buffer", "Hello "], ["reference", ["key", "type"], ["filters"]], ["buffer", " World!"]]'
    json_context = u'{\n  "type": function(chunk) {\n    return chunk.map(function(chunk) {\n      dust.nextTick(function() {\n        chunk.end("Async");\n      });\n    });\n  }\n}'
    rendered = u'Hello Async World!'
    context = {'type': async_key_func}


class EmptyArray(AshesTest):
    template = u'{#names}{title} {name}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "title"], ["filters"]], ["buffer", " "], ["reference", ["key", "name"], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": [], "title": "Sir"}'
    rendered = u''


class Escaped(AshesTest):
    template = u'{safe|s}{~n}{unsafe}'
    json_ast = '["body", ["reference", ["key", "safe"], ["filters", "s"]], ["special", "n"], ["reference", ["key", "unsafe"], ["filters"]]]'
    json_context = '{"safe": "<script>alert(\'Hello!\')</script>", "unsafe": "<script>alert(\'Goodbye!\')</script>"}'
    rendered = u"<script>alert('Hello!')</script>\n&lt;script&gt;alert('Goodbye!')&lt;/script&gt;"


class Partials(AshesTest):
    template = u'{>replace/} {>"plain"/} {>"{ref}"/}'
    json_ast = '["body", ["partial", ["literal", "replace"], ["context"]], ["buffer", " "], ["partial", ["literal", "plain"], ["context"]], ["buffer", " "], ["partial", ["body", ["reference", ["key", "ref"], ["filters"]]], ["context"]]]'
    json_context = '{"count": 42, "ref": "plain", "name": "Jim"}'
    rendered = u'Hello Jim! You have 42 new messages. Hello World! Hello World!'


class Recursion(AshesTest):
    template = u'{name}{~n}{#kids}{>recursion:./}{/kids}'
    json_ast = '["body", ["reference", ["key", "name"], ["filters"]], ["special", "n"], ["#", ["key", "kids"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["partial", ["literal", "recursion"], ["context", ["path", true, []]]]]]]]]'
    json_context = '{"kids": [{"kids": [{"name": "1.1.1"}], "name": "1.1"}], "name": "1"}'
    rendered = u'1\n1.1\n1.1.1'


class Array(AshesTest):
    template = u'{#names}{title} {name}{~n}{/names}'
    json_ast = '["body", ["#", ["key", "names"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "title"], ["filters"]], ["buffer", " "], ["reference", ["key", "name"], ["filters"]], ["special", "n"]]]]]]'
    json_context = '{"names": [{"name": "Moe"}, {"name": "Larry"}, {"name": "Curly"}], "title": "Sir"}'
    rendered = u'Sir Moe\nSir Larry\nSir Curly'


class Object(AshesTest):
    template = u'{#person}{root}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "root"], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = u'Subject: Larry, 45'


def filter_func(chunk, context, bodies, *a, **kw):
    return (chunk.tap(lambda data: data.upper())
            .render(bodies['block'], context)
            .untap())


class Filter(AshesTest):
    template = u'{#filter}foo {bar}{/filter}'
    json_ast = '["body", ["#", ["key", "filter"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "foo "], ["reference", ["key", "bar"], ["filters"]]]]]]]'
    json_context = u'{\n  "filter": function(chunk, context, bodies) {\n    return chunk.tap(function(data) {\n      return data.toUpperCase();\n    }).render(bodies.block, context).untap();\n  },\n  "bar": "bar"\n}'
    rendered = u'FOO BAR'
    context = {'filter': filter_func,
               'bar': 'bar'}


class ForceCurrent(AshesTest):
    template = u'{#person}{.root}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, ["root"]], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = u': Larry, 45'


class RenameKey(AshesTest):
    template = u'{#person foo=root}{foo}: {name}, {age}{/person}'
    json_ast = '["body", ["#", ["key", "person"], ["context"], ["params", ["param", ["literal", "foo"], ["key", "root"]]], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["key", "foo"], ["filters"]], ["buffer", ": "], ["reference", ["key", "name"], ["filters"]], ["buffer", ", "], ["reference", ["key", "age"], ["filters"]]]]]]]'
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = u'Subject: Larry, 45'


class InterpolatedParam(AshesTest):
    template = u'{#person foo="{root}_id"}{foo}: {name}, {age}{/person}'
    json_ast = u'''["body",["#",["key","person"],["context"],["params",["param",["literal","foo"],["body",["reference",["key","root"],["filters"]],["buffer","_id"]]]],["bodies",["param",["literal","block"],["body",["reference",["key","foo"],["filters"]],["buffer",": "],["reference",["key","name"],["filters"]],["buffer",", "],["reference",["key","age"],["filters"]]]]]]]'''
    json_context = '{"person": {"age": 45, "name": "Larry"}, "root": "Subject"}'
    rendered = u'Subject_id: Larry, 45'


class EscapePragma(AshesTest):
    template = u'{%esc:s}\n  {unsafe}{~n}\n  {%esc:h}\n    {unsafe}\n  {/esc}\n{/esc}'
    json_ast = r'["body",["%",["key","esc"],["context",["key","s"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["reference",["key","unsafe"],["filters"]],["special","n"],["format","\n","  "],["%",["key","esc"],["context",["key","h"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","    "],["reference",["key","unsafe"],["filters"]],["format","\n","  "]]]]],["format","\n",""]]]]]]'
    json_opt_ast = r'["body",["%",["key","esc"],["context",["key","s"]],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","unsafe"],["filters"]],["buffer","\n"],["%",["key","esc"],["context",["key","h"]],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","unsafe"],["filters"]]]]]]]]]]]'
    json_context = '{"unsafe": "<script>alert(\'Goodbye!\')</script>"}'
    rendered = '''<script>alert('Goodbye!')</script>\n&lt;script&gt;alert('Goodbye!')&lt;/script&gt;'''


class Intro(AshesTest):
    template = u'{#stream}{#delay}{.}{/delay}{/stream}'
    json_ast = '["body", ["#", ["key", "stream"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["#", ["key", "delay"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]]]]]]]'
    json_context = u'function() {\n  var d = 1;\n  return {\n    stream: function() {\n      return "asynchronous templates for the browser and node.js".split(\'\');\n    },\n    delay: function(chunk, context, bodies) {\n      return chunk.map(function(chunk) {\n        setTimeout(function() {\n          chunk.render(bodies.block, context).end();\n        }, d++ * 15);\n      });\n    }\n  }\n}'


class BaseTemplate(AshesTest):
    template = u'Start{~n}\n{+title}\n  Base Title\n{/title}\n{~n}\n{+main}\n  Base Content\n{/main}\n{~n}\nEnd'
    json_ast = '["body", ["buffer", "Start"], ["special", "n"], ["format", "\\n", ""], ["+", ["key", "title"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Base Title"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["+", ["key", "main"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Base Content"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["buffer", "End"]]'
    json_context = '{}'
    rendered = u'Start\nBase Title\nBase Content\nEnd'


class AsyncIterator(AshesTest):
    template = u'{#numbers}{#delay}{.}{/delay}{@sep}, {/sep}{/numbers}'
    json_ast = '["body", ["#", ["key", "numbers"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["#", ["key", "delay"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["reference", ["path", true, []], ["filters"]]]]]], ["@", ["key", "sep"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", ", "]]]]]]]]]]'
    json_context = u'{\n  "numbers": [\n  3, 2, 1],\n  "delay": function(chunk, context, bodies) {\n    return chunk.map(function(chunk) {\n      setTimeout(function() {\n        chunk.render(bodies.block, context).end();\n      }, Math.ceil(Math.random() * 10));\n    });\n  }\n}'
    rendered = u'3, 2, 1'


class ElseBlock(AshesTest):
    template = u'{#foo}\n  foo,{~s}\n{:else}\n  not foo,{~s}\n{/foo}\n{#bar}\n  bar!\n{:else}\n  not bar!\n{/bar}'
    json_ast = '["body", ["#", ["key", "foo"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "not foo,"], ["special", "s"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "foo,"], ["special", "s"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["#", ["key", "bar"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "not bar!"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "bar!"], ["format", "\\n", ""]]]]]]'
    json_context = '{"foo": true, "bar": false}'
    rendered = u'foo, not bar!'


class Context(AshesTest):
    template = u'{#list:projects}{name}{:else}No Projects!{/list}'
    json_ast = '["body", ["#", ["key", "list"], ["context", ["key", "projects"]], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "No Projects!"]]], ["param", ["literal", "block"], ["body", ["reference", ["key", "name"], ["filters"]]]]]]]'
    json_context = u'{\n  "list": function(chunk, context, bodies) {\n    var items = context.current(),\n        len = items.length;\n\n    if (len) {\n      chunk.write("<ul>\\n");\n      for (var i = 0; i < len; i++) {\n        chunk = chunk.write("<li>").render(bodies.block, context.push(items[i])).write("</li>\\n");\n      }\n      return chunk.write("</ul>");\n    } else if (bodies[\'else\']) {\n      return chunk.render(bodies[\'else\'], context);\n    }\n    return chunk;\n  },\n  "projects": [{\n    "name": "Mayhem"\n  },\n  {\n    "name": "Flash"\n  },\n  {\n    "name": "Thunder"\n  }]\n}'
    rendered = u'<ul>\n<li>Mayhem</li>\n<li>Flash</li>\n<li>Thunder</li>\n</ul>'


class ChildTemplate(AshesTest):
    template = u'{^xhr}\n  {>base_template/}\n{:else}\n  {+main/}\n{/xhr}\n{<title}\n  Child Title\n{/title}\n{<main}\n  Child Content\n{/main}\n'
    json_ast = '["body", ["^", ["key", "xhr"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["+", ["key", "main"], ["context"], ["params"], ["bodies"]], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["partial", ["literal", "base_template"], ["context"]], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["<", ["key", "title"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Child Title"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["<", ["key", "main"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "Child Content"], ["format", "\\n", ""]]]]], ["format", "\\n", ""]]'
    json_context = '{"xhr": false}'
    rendered = u'Start\nChild Title\nChild Content\nEnd'


class Conditional(AshesTest):
    template = u'{?tags}\n  <ul>{~n}\n    {#tags}\n      {~s} <li>{.}</li>{~n}\n    {/tags}\n  </ul>\n{:else}\n  No Tags!\n{/tags}\n{~n}\n{^likes}\n  No Likes!\n{:else}\n  <ul>{~n}\n    {#likes}\n      {~s} <li>{.}</li>{~n}\n    {/likes}\n  </ul>\n{/likes}'
    json_ast = '["body", ["?", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "No Tags!"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "<ul>"], ["special", "n"], ["format", "\\n", "    "], ["#", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "      "], ["special", "s"], ["buffer", " <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>"], ["special", "n"], ["format", "\\n", "    "]]]]], ["format", "\\n", "  "], ["buffer", "</ul>"], ["format", "\\n", ""]]]]], ["format", "\\n", ""], ["special", "n"], ["format", "\\n", ""], ["^", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["format", "\\n", "  "], ["buffer", "<ul>"], ["special", "n"], ["format", "\\n", "    "], ["#", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["format", "\\n", "      "], ["special", "s"], ["buffer", " <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>"], ["special", "n"], ["format", "\\n", "    "]]]]], ["format", "\\n", "  "], ["buffer", "</ul>"], ["format", "\\n", ""]]], ["param", ["literal", "block"], ["body", ["format", "\\n", "  "], ["buffer", "No Likes!"], ["format", "\\n", ""]]]]]]'
    json_opt_ast = '["body", ["?", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "No Tags!"]]], ["param", ["literal", "block"], ["body", ["buffer", "<ul>\\n"], ["#", ["key", "tags"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "  <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>\\n"]]]]], ["buffer", "</ul>"]]]]], ["buffer", "\\n"], ["^", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "else"], ["body", ["buffer", "<ul>\\n"], ["#", ["key", "likes"], ["context"], ["params"], ["bodies", ["param", ["literal", "block"], ["body", ["buffer", "  <li>"], ["reference", ["path", true, []], ["filters"]], ["buffer", "</li>\\n"]]]]], ["buffer", "</ul>"]]], ["param", ["literal", "block"], ["body", ["buffer", "No Likes!"]]]]]]'
    json_context = '{"likes": ["moe", "larry", "curly", "shemp"], "tags": []}'
    rendered = u'No Tags!\n<ul>\n  <li>moe</li>\n  <li>larry</li>\n  <li>curly</li>\n  <li>shemp</li>\n</ul>'
