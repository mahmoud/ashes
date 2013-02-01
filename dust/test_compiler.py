from dust import DustEnv

from tests.ref_templates import ref_templates


def main_c(tmpl_name):
    tmpl = ref_templates[tmpl_name]
    env = DustEnv()
    comp_str = env.compile(tmpl, tmpl_name)
    print comp_str
    import pdb;pdb.set_trace()
    return comp_str

if __name__ == '__main__':
    try:
        main_c('else_block')
        #see_passing_asts()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
