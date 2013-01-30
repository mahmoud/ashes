from pprint import pprint

from dust import CompileContext, ParseTree, Optimizer

from tests.ref_templates import ref_templates


def main_c(tmpl_name):
    tmpl = ref_templates[tmpl_name]
    parse_tree = ParseTree.from_source(tmpl)
    optimized_ast = Optimizer()(parse_tree.to_dust_ast())
    comp_str = CompileContext().compile(optimized_ast)
    print comp_str
    import pdb;pdb.set_trace()
    return comp_str

if __name__ == '__main__':
    try:
        main_c('conditional')
        #see_passing_asts()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
