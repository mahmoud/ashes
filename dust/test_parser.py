from pprint import pprint
import json

from dust import tokenize, ParseTree, Optimizer

from tests.ref_templates import ref_templates
from tests.ref_opt_asts import ref_opt_asts
from tests.ref_asts import ref_asts

DEFAULT_TMPL_NAME = 'conditional'


def main_t():
    #pprint(parse_ref['plain'])
    #pprint(tokenize(parse_tests['implicit']))
    print
    for k, v in ref_templates.items():
        print
        print k
        pprint(tokenize(ref_templates[k]))
        print
        pprint(v)


def t_and_p(text):
    return ParseTree.from_source(text)


def see_ref_asts():
    for k, v in ref_templates.items():
        print
        print k
        print
        if k in ref_asts:
            pprint(ref_asts[k])
            print
        print '------------'
    return


def main_opt_p():
    optimize = Optimizer()
    for k, v in ref_templates.items():
        if k not in ref_opt_asts:
            continue
        parse_tree = t_and_p(ref_templates[k])
        my_ast = json_roundtrip(parse_tree.to_dust_ast())
        my_opt_ast = optimize(my_ast)
        if json_indent(my_opt_ast) == json_indent(ref_opt_asts[k]):
            print k, 'passed.'
        else:
            pprint(ref_opt_asts[k])
            print '--------'
            pprint(my_opt_ast)
    print


def see_passing_asts():
    successful = []
    failed = []
    for k, v in ref_templates.items():
        if k not in ref_asts:
            continue
        try:
            parse_tree = t_and_p(ref_templates[k])
            my_ast = json_roundtrip(parse_tree.to_dust_ast())
        except:
            failed.append(k)
            continue
        if my_ast == ref_asts[k]:
            successful.append(k)
        else:
            failed.append(k)
    print
    print ' Successful:', successful
    print ' Failed:', failed
    print
    print 'Overall:', len(successful), '/', len(successful) + len(failed)
    print

    return successful, failed


def json_indent(obj):
    if isinstance(obj, basestring):
        obj = json.loads(obj)
    return json.dumps(obj, indent=2)


def json_pprint(obj):
    print json_indent(obj)


def json_roundtrip(obj):
    return json.loads(json.dumps(obj))


def main_p(tmpl_name=DEFAULT_TMPL_NAME):
    try:
        pprint(ref_asts[tmpl_name])
    except KeyError:
        print '(no reference)'
    print
    parse_tree = t_and_p(ref_templates[tmpl_name])
    #pprint(parse_tree.root_block.to_list())
    print '\n----------\n'
    my_ast = json_roundtrip(parse_tree.to_dust_ast())
    pprint(my_ast)

    print my_ast == ref_asts[tmpl_name]


if __name__ == '__main__':
    try:
        main_opt_p()  # 'conditional')
        see_passing_asts()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
