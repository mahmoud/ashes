from dust import DustEnv

from tests.ref_templates import ref_templates
from tests.ref_renders import ref_renders
from tests.ref_contexts import ref_contexts


def main_r(tmpl_name):
    tmpl = ref_templates[tmpl_name]
    env = DustEnv()
    env.compile(tmpl, tmpl_name)
    print ref_contexts[tmpl_name]
    render_str = env.render(tmpl_name, ref_contexts[tmpl_name])
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
            print 'Exception: ', k
            failed.append(k)
            continue
        if render_str.strip() == ref_renders[k].strip():
            successful.append(k)
        else:
            print k, 'did not match:'
            print '"' + render_str.strip() + '"'
            print '"' + ref_renders[k].strip() + '"'
            print
            failed.append(k)
    print
    print ' Successful:', successful
    print ' Failed:', failed
    print
    print 'Overall:', len(successful), '/', len(successful) + len(failed)
    print

if __name__ == '__main__':
    try:
        #main_r('object')
        see_passing_renders()
    except Exception as e:
        import pdb;pdb.post_mortem()
        raise
