"""
this uses a custom loader to test different ways of laoding data

it was used more for API/interface development and testing

toggle the ``OPTIMIZE_VIA`` variable to test the different kinds

note that the globalCache is used to save the data, and then templates are generated
off of that


"""
import logging
log = logging.getLogger(__name__)

import ashes
import simplejson as json
import pdb
import pprint
import os
import os.path

# ==============================================================================
# ==============================================================================

DEBUG_TEMPLATE_LOADING = True
OPTIMIZE_VIA = 'python_compiled'  # ['template', 'ast', 'python_string', 'python_compiled']

# ==============================================================================
# ==============================================================================

ashes__default_env = ashes.AshesEnv(keep_whitespace=True)

globalCache = {
    'template': {},
    'ast': {},
    'python_string': {},
    'python_compiled': {},
}

class CustomAshesLoader(object):
    """Class for Ashes (dust.js in Python) template loading.
        This is a support class, used to proxy missing template requests by the Ashes environment into our custom template loader.
    """

    def __init__(self, root_path, exts=None, encoding='utf-8'):
        self.root_path = os.path.normpath(root_path)
        self.encoding = encoding

    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("CustomAshesLoader.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type
        if OPTIMIZE_VIA == 'template':
            if abs_path in globalCache['template']:
                log.debug("using globalCache['template']['%s']" % abs_path)
                return globalCache['template'][abs_path]
        elif OPTIMIZE_VIA == 'ast':
            if abs_path in globalCache['ast']:
                log.debug("using globalCache['ast']['%s']" % abs_path)
                ast = globalCache['ast'][abs_path]
                template = template_type.from_ast(name=template_name,
                                               ast=ast,
                                               env=env)   
                return template
        elif OPTIMIZE_VIA == 'python_string':
            if abs_path in globalCache['python_string']:
                log.debug("using globalCache['python_string']['%s']" % abs_path)
                python_string = globalCache['python_string'][abs_path]
                template = template_type.from_python_string(name=template_name,
                                               python_string=python_string,
                                               env=env)   
                return template
        elif OPTIMIZE_VIA == 'python_compiled':
            if abs_path in globalCache['python_compiled']:
                log.debug("using globalCache['python_compiled']['%s']" % abs_path)
                python_string_compiled = globalCache['python_compiled'][abs_path]
                template = template_type.from_python_compiled(name=template_name,
                                               python_compiled=python_string_compiled,
                                               env=env)   
                return template
        if OPTIMIZE_VIA == 'template':
            print "name=template_name (%s)" % template_name
            print "path=abs_path (%s)" % abs_path
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)        
            globalCache['template'][abs_path] = template
        elif OPTIMIZE_VIA == 'ast':
            # load it first
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            ast = template.to_ast()
            globalCache['ast'][abs_path] = ast
        elif OPTIMIZE_VIA == 'python_string':
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            python_string = template.to_python_string()
            globalCache['python_string'][abs_path] = python_string
        elif OPTIMIZE_VIA == 'python_compiled':
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            python_string = template.to_python_string()
            python_string_compiled = ashes.compile_python_string(python_string)
            globalCache['python_compiled'][abs_path] = python_string_compiled
        return template


def test_1(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== test_1 | %s" % iteration)
    ashesLoader = CustomAshesLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), keep_whitespace=True)
    templated = ashesEnv.render('all.dust', {})
    # print templated


if __name__ == '__main__':
    log.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)
    for i in range(1,10):
        test_1(i)
