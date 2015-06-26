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

import tests_jv_utils

# ==============================================================================
# ==============================================================================

DEBUG_TEMPLATE_LOADING = True
OPTIMIZE_VIA = 'python_compiled'  # ['template', 'ast', 'python_string', 'python_compiled']
ITERATIONS = 1000

# ==============================================================================
# ==============================================================================

ashes__default_env = ashes.AshesEnv()

globalCache = {
    'template': {},
    'ast': {},
    'python_string': {},
    'python_compiled': {},
}


class CustomAshesLoader(object):
    """Class for Ashes (dust.js in Python) template loading.
        This is a support class, used to proxy missing template requests by the Ashes environment into our custom template loader.
        This probably should have been 4 different loaders.  oh well!
    """

    def __init__(self, root_path, exts=None, encoding='utf-8'):
        self.root_path = os.path.normpath(root_path)
        self.encoding = encoding


class LoaderStd(CustomAshesLoader):
    """this does a normal load"""
    
    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("LoaderStd.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type

        template = template_type.from_path(name=template_name,
                                           path=abs_path,
                                           encoding=self.encoding,
                                           keep_source=True,
                                           env=env)
        return template


class LoaderTemplate(CustomAshesLoader):
    """this caches template objects"""

    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("LoaderTemplate.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type

        if abs_path in globalCache['template']:
            log.debug("using globalCache['template']['%s']" % abs_path)
            template = globalCache['template'][abs_path]
        else:
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source=True,
                                               env=env)
            globalCache['template'][abs_path] = template
        return template


class LoaderAST(CustomAshesLoader):
    """this caches template AST"""

    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("LoaderAST.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type

        if abs_path in globalCache['ast']:
            log.debug("using globalCache['ast']['%s']" % abs_path)
            ast = globalCache['ast'][abs_path]
            template = template_type.from_ast(name=template_name,
                                              ast=ast,
                                              env=env)
        else:
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            ast = template.to_ast()
            globalCache['ast'][abs_path] = ast
        return template


class LoaderPythonString(CustomAshesLoader):
    """this caches template python strings"""

    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("LoaderPythonString.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type

        if abs_path in globalCache['python_string']:
            log.debug("using globalCache['python_string']['%s']" % abs_path)
            python_string = globalCache['python_string'][abs_path]
            template = template_type.from_python_string(name=template_name,
                                                        python_string=python_string,
                                                        env=env)
        else:
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            python_string = template.to_python_string()
            globalCache['python_string'][abs_path] = python_string
        return template


class LoaderPythonCompiled(CustomAshesLoader):
    """this caches template python defs (compiled)"""

    def load(self, path, env=None):
        if DEBUG_TEMPLATE_LOADING:
            log.debug("LoaderPythonCompiled.load('%s')" % path)
        env = env or ashes__default_env
        norm_path = os.path.normpath(path)
        if path.startswith('../'):
            raise ValueError('no traversal above loader root path: %r' % path)
        if not path.startswith(self.root_path):
            norm_path = os.path.join(self.root_path, norm_path)
        abs_path = os.path.abspath(norm_path)
        template_name = os.path.relpath(abs_path, self.root_path)
        template_type = env.template_type

        if abs_path in globalCache['python_compiled']:
            log.debug("using globalCache['python_compiled']['%s']" % abs_path)
            python_string_compiled = globalCache['python_compiled'][abs_path]
            template = template_type.from_python_compiled(name=template_name,
                                                          python_compiled=python_string_compiled,
                                                          env=env)
        else:
            template = template_type.from_path(name=template_name,
                                               path=abs_path,
                                               encoding=self.encoding,
                                               keep_source = True,
                                               env=env)
            python_string = template.to_python_string()
            python_string_compiled = ashes.compile_python_string(python_string)
            globalCache['python_compiled'][abs_path] = python_string_compiled
        return template


@tests_jv_utils.timeit
def test_LoaderStd(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== LoaderStd | %s" % iteration)
    ashesLoader = LoaderStd('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), )
    templated = ashesEnv.render('all.dust', {})


@tests_jv_utils.timeit
def test_Template(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== test_Template | %s" % iteration)
    ashesLoader = LoaderTemplate('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), )
    templated = ashesEnv.render('all.dust', {})


@tests_jv_utils.timeit
def test_AST(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== test_AST | %s" % iteration)
    ashesLoader = LoaderAST('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), )
    templated = ashesEnv.render('all.dust', {})


@tests_jv_utils.timeit
def test_PythonString(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== test_PythonString | %s" % iteration)
    ashesLoader = LoaderPythonString('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), )
    templated = ashesEnv.render('all.dust', {})


@tests_jv_utils.timeit
def test_PythonCompiled(iteration=1):
    if DEBUG_TEMPLATE_LOADING:
        log.debug("===================== test_PythonCompiled | %s" % iteration)
    ashesLoader = LoaderPythonCompiled('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader,), )
    templated = ashesEnv.render('all.dust', {})


if __name__ == '__main__':
    if False:
        log.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        log.addHandler(ch)

    for i in range(1, ITERATIONS):
        test_LoaderStd(i)

    for i in range(1, ITERATIONS):
        test_Template(i)

    for i in range(1, ITERATIONS):
        test_AST(i)

    for i in range(1, ITERATIONS):
        test_PythonString(i)

    for i in range(1, ITERATIONS):
        test_PythonCompiled(i)

    tests_jv_utils.timed_stats()
