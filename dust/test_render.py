from dust import DustEnv

from tests.ref_templates import ref_templates


def main_r(tmpl_name):
    tmpl = ref_templates[tmpl_name]
    env = DustEnv()
    env.compile(tmpl, tmpl_name)
    render_str = env.render(tmpl_name, {})
    print render_str
    import pdb;pdb.set_trace()
    return render_str

if __name__ == '__main__':
    try:
        main_r('conditional')
        #see_passing_asts()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
