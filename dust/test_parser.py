import json
from pprint import pprint

from dust import tokenize, ParseTree

DEFAULT_TMPL_NAME = 'conditional'

parse_tests = {
    'plain': 'Hello World!',
    'replace': 'Hello {name}! You have {count} new messages.',
    'array': '{#names}{title} {name}{~n}{/names}',
    'path': '{foo.bar}',
    'context': '{#list:projects}{name}{:else}No Projects!{/list}',
    'params': '{#helper foo="bar"/}',
    'easy_nest': '{#names}hi{/names}',
    'p_and_r': '{foo.bar} {name}',
    'implicit': '{#names}{.}{~n}{/names}',
    'conditional': '''
{?tags}
  <ul>{~n}
    {#tags}
      {~s} <li>{.}</li>{~n}
    {/tags}
  </ul>
{:else}
  No Tags!
{/tags}
{~n}
{^likes}
  No Likes!
{:else}
  <ul>{~n}
    {#likes}
      {~s} <li>{.}</li>{~n}
    {/likes}
  </ul>
{/likes}'''}

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
    'path': '["body",["reference",["path",false,["foo","bar"]],["filters"]]]',
    'p_and_r': '''["body",["reference",["path",false,["foo","bar"]],
                  ["filters"]],["buffer"," "],["reference",
                  ["key","name"],["filters"]]]''',
    'context': '''["body",["#",["key","list"],["context",["key","projects"]],
                  ["params"],["bodies",["param",["literal","else"],["body",
                  ["buffer","No Projects!"]]],["param",["literal","block"],
                  ["body",["reference",["key","name"],["filters"]]]]]]]''',
    'params': '''["body",["#",["key","helper"],["context"],["params",["param",
                 ["literal","foo"],["literal","bar"]]],["bodies"]]]''',
    'implicit': '''["body",["#",["key","names"],["context"],["params"],
                   ["bodies",["param",["literal","block"],
                   ["body",["reference",["path",true,[]],
                   ["filters"]],["special","n"]]]]]]''',
    'conditional': '''["body",["?",["key","tags"],["context"],["params"],
                      ["bodies",["param",["literal","else"],["body",["format",
                      "\\n"," "], ["buffer","No Tags!"],["format",
                      "\\n",""]]],["param",["literal","block"],["body",
                      ["format","\\n"," "],["buffer","<ul>"],
                      ["special","n"],["format","\\n"," "],["#",["key",
                      "tags"],["context"],
                      ["params"],["bodies",["param",["literal","block"],
                      ["body",["format","\\n"," "],["special","s"],
                      ["buffer","<li>"],["reference",["path",true,[]],
                      ["filters"]],["buffer","</li>"],["special","n"],
                      ["format","\\n"," "]]]]],["format","\\n"," "],
                      ["buffer","</ul>"],["format","\\n",""]]]]],["format",
                      "\\n", ""],
                      ["special","n"],["format","\\n",""],["^",["key","likes"],
                      ["context"],
                      ["params"],["bodies",["param",["literal","else"],["body",
                      ["format","\\n",""],["buffer","<ul>"],["special","n"],
                      ["format","\\n"," "],["#",["key","likes"],["context"],
                      ["params"],["bodies",["param",["literal","block"],
                      ["body",["format","\\n",""],["special","s"],["buffer",
                      "<li>"],["reference",["path",true,[]],["filters"]],
                      ["buffer","</li>"],["special","n"],["format","\\n",
                      ""]] ]]],["format","\\n",
                      ""],["buffer","</ul>"],["format","\\n",""]]],
                      ["param",["literal","block"],["body",["format","\\n",
                      ""], ["buffer","No Likes!"],["format","\\n",""]]]]]]'''
    }

parse_ref = dict([(k, json.loads(v)) for k, v
                      in parse_ref_json.items()])


def main_t():
    #pprint(parse_ref['plain'])
    #pprint(tokenize(parse_tests['implicit']))
    print
    for k, v in parse_ref.items():
        print
        print k
        pprint(tokenize(parse_tests[k]))
        print
        pprint(v)


def t_and_p(text):
    return ParseTree.from_source(text)


def see_ref_asts():
    for k, v in parse_ref.items():
        print
        print k
        if k in parse_tests:
            print parse_tests[k]
            print
        pprint(v)
        print
        print '------------'
    return


def main_p(tmpl_name=DEFAULT_TMPL_NAME):
    try:
        pass  # pprint(parse_ref[tmpl_name])
    except KeyError:
        print '(no reference)'
    print
    #pprint(tokenize(parse_tests[tmpl_name]))
    #print
    parse_tree = t_and_p(parse_tests[tmpl_name])
    pprint(parse_tree.root_block.to_list())
    print '\n----------\n'
    pprint(parse_tree.to_dust_ast())


if __name__ == '__main__':
    try:
        main_p()
        #see_ref_asts()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
