from __future__ import unicode_literals

import json

INTRO = r'''["body",["#",["key","stream"],["context"],["params"],["bodies",["param",["literal","block"],["body",["#",["key","delay"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["path",true,[]],["filters"]]]]]]]]]]]'''

PLAIN = r'''["body",["buffer","Hello World!"]]'''

REPLACE = r'''["body",["buffer","Hello "],["reference",["key","name"],["filters"]],["buffer","! You have "],["reference",["key","count"],["filters"]],["buffer"," new messages."]]'''

ZERO = r'''["body",["#",["key","zero"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["path",true,[]],["filters"]]]]]]]'''

ARRAY = r'''["body",["#",["key","names"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","title"],["filters"]],["buffer"," "],["reference",["key","name"],["filters"]],["special","n"]]]]]]'''

EMPTY_ARRAY = ARRAY

IMPLICIT = r'''["body",["#",["key","names"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["path",true,[]],["filters"]],["special","n"]]]]]]'''

OBJECT = r'''["body",["#",["key","person"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["key","root"],["filters"]],["buffer",": "],["reference",["key","name"],["filters"]],["buffer",", "],["reference",["key","age"],["filters"]]]]]]]'''

RENAME_KEY = r'''["body",["#",["key","person"],["context"],["params",["param",["literal","foo"],["key","root"]]],["bodies",["param",["literal","block"],["body",["reference",["key","foo"],["filters"]],["buffer",": "],["reference",["key","name"],["filters"]],["buffer",", "],["reference",["key","age"],["filters"]]]]]]]'''

FORCE_CURRENT = r'''["body",["#",["key","person"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["path",true,["root"]],["filters"]],["buffer",": "],["reference",["key","name"],["filters"]],["buffer",", "],["reference",["key","age"],["filters"]]]]]]]'''

PATH = r'''["body",["reference",["path",false,["foo","bar"]],["filters"]]]'''

ESCAPED = r'''["body",["reference",["key","safe"],["filters","s"]],["special","n"],["reference",["key","unsafe"],["filters"]]]'''

ESCAPE_PRAGMA = r'''["body",["%",["key","esc"],["context",["key","s"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["reference",["key","unsafe"],["filters"]],["special","n"],["format","\n","  "],["%",["key","esc"],["context",["key","h"]],["params"],["bodies",["param",["literal","block"],["body",["format","\n","    "],["reference",["key","unsafe"],["filters"]],["format","\n","  "]]]]],["format","\n",""]]]]]]'''

ELSE_BLOCK = r'''["body",["#",["key","foo"],["context"],["params"],["bodies",["param",["literal","else"],["body",["format","\n","  "],["buffer","not foo,"],["special","s"],["format","\n",""]]],["param",["literal","block"],["body",["format","\n","  "],["buffer","foo,"],["special","s"],["format","\n",""]]]]],["format","\n",""],["#",["key","bar"],["context"],["params"],["bodies",["param",["literal","else"],["body",["format","\n","  "],["buffer","not bar!"],["format","\n",""]]],["param",["literal","block"],["body",["format","\n","  "],["buffer","bar!"],["format","\n",""]]]]]]'''

CONDITIONAL = r'''["body",["?",["key","tags"],["context"],["params"],["bodies",["param",["literal","else"],["body",["format","\n","  "],["buffer","No Tags!"],["format","\n",""]]],["param",["literal","block"],["body",["format","\n","  "],["buffer","<ul>"],["special","n"],["format","\n","    "],["#",["key","tags"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","      "],["special","s"],["buffer"," <li>"],["reference",["path",true,[]],["filters"]],["buffer","</li>"],["special","n"],["format","\n","    "]]]]],["format","\n","  "],["buffer","</ul>"],["format","\n",""]]]]],["format","\n",""],["special","n"],["format","\n",""],["^",["key","likes"],["context"],["params"],["bodies",["param",["literal","else"],["body",["format","\n","  "],["buffer","<ul>"],["special","n"],["format","\n","    "],["#",["key","likes"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","      "],["special","s"],["buffer"," <li>"],["reference",["path",true,[]],["filters"]],["buffer","</li>"],["special","n"],["format","\n","    "]]]]],["format","\n","  "],["buffer","</ul>"],["format","\n",""]]],["param",["literal","block"],["body",["format","\n","  "],["buffer","No Likes!"],["format","\n",""]]]]]]'''

SYNC_KEY = r'''["body",["buffer","Hello "],["reference",["key","type"],["filters"]],["buffer"," World!"]]'''

ASYNC_KEY = SYNC_CHUNK = SYNC_KEY

ASYNC_ITERATOR = r'''["body",["#",["key","numbers"],["context"],["params"],["bodies",["param",["literal","block"],["body",["#",["key","delay"],["context"],["params"],["bodies",["param",["literal","block"],["body",["reference",["path",true,[]],["filters"]]]]]],["@",["key","sep"],["context"],["params"],["bodies",["param",["literal","block"],["body",["buffer",", "]]]]]]]]]]'''

FILTER = r'''["body",["#",["key","filter"],["context"],["params"],["bodies",["param",["literal","block"],["body",["buffer","foo "],["reference",["key","bar"],["filters"]]]]]]]'''

CONTEXT = r'''["body",["#",["key","list"],["context",["key","projects"]],["params"],["bodies",["param",["literal","else"],["body",["buffer","No Projects!"]]],["param",["literal","block"],["body",["reference",["key","name"],["filters"]]]]]]]'''

PARAMS = r'''["body",["#",["key","helper"],["context"],["params",["param",["literal","foo"],["literal","bar"]]],["bodies"]]]'''

PARTIALS = r'''["body",["partial",["literal","replace"],["context"]],["buffer"," "],["partial",["literal","plain"],["context"]],["buffer"," "],["partial",["body",["reference",["key","ref"],["filters"]]],["context"]]]'''

PARTIAL_CONTEXT = r'''["body",["partial",["literal","replace"],["context",["path",true,["profile"]]]]]'''

BASE_TEMPLATE = r'''["body",["buffer","Start"],["special","n"],["format","\n",""],["+",["key","title"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["buffer","Base Title"],["format","\n",""]]]]],["format","\n",""],["special","n"],["format","\n",""],["+",["key","main"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["buffer","Base Content"],["format","\n",""]]]]],["format","\n",""],["special","n"],["format","\n",""],["buffer","End"]]'''

CHILD_TEMPLATE = r'''["body",["^",["key","xhr"],["context"],["params"],["bodies",["param",["literal","else"],["body",["format","\n","  "],["+",["key","main"],["context"],["params"],["bodies"]],["format","\n",""]]],["param",["literal","block"],["body",["format","\n","  "],["partial",["literal","base_template"],["context"]],["format","\n",""]]]]],["format","\n",""],["<",["key","title"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["buffer","Child Title"],["format","\n",""]]]]],["format","\n",""],["<",["key","main"],["context"],["params"],["bodies",["param",["literal","block"],["body",["format","\n","  "],["buffer","Child Content"],["format","\n",""]]]]],["format","\n",""]]'''

RECURSION = r'''["body",["reference",["key","name"],["filters"]],["special","n"],["#",["key","kids"],["context"],["params"],["bodies",["param",["literal","block"],["body",["partial",["literal","recursion"],["context",["path",true,[]]]]]]]]]'''

COMMENTS = r'''["body",["comment","\n  Multiline\n  {#foo}{bar}{/foo}\n"],["format","\n",""],["comment","before"],["buffer","Hello"],["comment","after"]]'''

ref_asts = {}
_globals = globals()
try:
    for name, json_source in _globals.items():
        if not name.isupper() or name.startswith('_'):
            continue
        json_escaped = json_source.replace('\\', '\\\\')
        ref_asts[name.lower()] = json.loads(json_escaped)
        _globals[name] = json_escaped
finally:
    del _globals


if __name__ == '__main__':
    print 'known ASTs:', ref_asts.keys()
