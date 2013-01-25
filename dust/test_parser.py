import json
from pprint import pprint
from sys import stderr


from dust import tokenize
from parser import Parser

DEFAULT_TMPL_NAME = 'p_and_r'

parse_tests = {
    'plain': 'Hello World!',
    'replace': 'Hello {name}! You have {count} new messages.',
    'array': '{#names}{title} {name}{~n}{/names}',
    'path': '{foo.bar}',
    'context': '{#list:projects}{name}{:else}No Projects!{/list}',
    'params': '{#helper foo="bar"/}',
    'easy_nest': '{#names}hi{/names}',
    'p_and_r': '{foo.bar} {name}',
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
                   ["filters"]],["special","n"]]]]]]'''
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
    return

def t_and_p(text):
    p = Parser()
    tokens = tokenize(text)
    try:
        tree = p.parse(tokens)
    except p.ParseErrors, e:
        for token,expected in e.errors:
            if token[0] == p.EOF:
                print >>stderr, "unexpected end of file"
                continue

            found = repr(token[0])
            if len(expected) == 1:
                msg = "missing %s (found %s)"%(repr(expected[0]), found)
            else:
                msg1 = "parse error before %s, "%found
                l = sorted([ repr(s) for s in expected ])
                msg2 = "expected one of "+", ".join(l)
                msg = msg1+msg2
            print >>stderr, msg
        raise
    return tree

def main_p(tmpl_name=DEFAULT_TMPL_NAME):
    try:
        pprint(parse_ref[tmpl_name])
    except KeyError:
        print '(no reference)'
    print
    pprint(tokenize(parse_tests[tmpl_name]))
    print
    pprint(t_and_p(parse_tests[tmpl_name]))

if __name__ == '__main__':
    try:
        main_p()
    except Exception as e:
        import pdb;pdb.post_mortem()
