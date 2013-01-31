from dust import DustEnv

from tests.ref_templates import ref_templates
from tests.ref_renders import ref_renders
from tests.ref_contexts import ref_contexts


def main_r(tmpl_name):
    tmpl = ref_templates[tmpl_name]
    env = DustEnv()
    env.compile(tmpl, tmpl_name)
    render_str = env.render(tmpl_name, DEFAULT_CONTEXT)
    print render_str
    import pdb;pdb.set_trace()
    return render_str


def see_passing_renders():
    successful = []
    failed = []
    for k, v in ref_templates.items():
        if k not in ref_renders or k not in ref_contexts:
            continue
        try:
            env = DustEnv()
            env.compile(v, k)
            render_str = env.render(k, ref_contexts[k])
        except:
            failed.append(k)
            continue
        if render_str == ref_renders[k]:
            successful.append(k)
        else:
            failed.append(k)
    print
    print ' Successful:', successful
    print ' Failed:', failed
    print
    print 'Overall:', len(successful), '/', len(successful) + len(failed)
    print

if __name__ == '__main__':
    try:
        #main_r('conditional')
        see_passing_renders()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
