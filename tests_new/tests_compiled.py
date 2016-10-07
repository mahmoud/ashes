"""
This is just a quick file to bench test the various ways of loading data


"""

import pprint
import tests_compiled_utils as utils
import ashes

import os
import hashlib

from tests_compiled_loaders import TemplatePathLoaderExtended

# ==============================================================================
# ==============================================================================


ITERATIONS = 100
PRINT_SAMPLE = False
templates_directory = '../tests/'


EXPORT = False
if EXPORT:
    EXPORTS_DIR = 'output'
    if not os.path.exists(EXPORTS_DIR):
        os.mkdir(EXPORTS_DIR)

# ==============================================================================
# ==============================================================================


@utils.timeit
def test_baseline(i):
    """
    test_baseline
    this should be the longest and the normal ashes behavior
    """
    ashesLoader = ashes.TemplatePathLoader('%stemplates_a' % templates_directory)
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    templated = ashesEnv.render('oranges.dust', {})
    return templated

for i in range(0, ITERATIONS):
    rendered_oranges = test_baseline(i)

rendered_oranges_baseline = rendered_oranges

if EXPORT:
    open("%s/oranges-output.html" % EXPORTS_DIR, "w").write(rendered_oranges_baseline)
if PRINT_SAMPLE:
    print "========================"
    print "Normal method"
    utils.print_timed()
    print rendered_oranges_baseline
    print "========================"

# ==============================================================================
# ==============================================================================

# test a loaded ast method

ashesLoader = TemplatePathLoaderExtended('%stemplates_a' % templates_directory)
ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
ast__oranges = ashesEnv.load('oranges.dust').to_ast()
ast__apples = ashesEnv.load('apples.dust').to_ast()

if PRINT_SAMPLE:
    print "========================"
    print "ast__apples = '''", ast__apples, "'''"
    print "ast__oranges = '''", ast__oranges, "'''"
    print "========================"

if EXPORT:
    open("%s/apples-ast.txt" % EXPORTS_DIR, "w").write(str(ast__apples))
    open("%s/oranges-ast.txt" % EXPORTS_DIR, "w").write(str(ast__oranges))

@utils.timeit
def test_ast():
    """with the AST test, we should be preloading the ast"""
    ashesLoader = TemplatePathLoaderExtended('%stemplates_a' % templates_directory)
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    ashesEnv.register(ashesLoader.load_precompiled('apples.dust', source_ast=ast__apples),
                      name="apples.dust",
                      )
    ashesEnv.register(ashesLoader.load_precompiled('oranges.dust', source_ast=ast__oranges),
                      name='oranges.dust',
                      )
    templated = ashesEnv.render('oranges.dust', {})
    return templated

for i in range(0, ITERATIONS):
    rendered_oranges = test_ast()

rendered_oranges_ast = rendered_oranges

if PRINT_SAMPLE:
    print "========================"
    print "Loaded AST method"
    utils.print_timed()
    print rendered_oranges_ast
    print "========================"


# ==============================================================================
# ==============================================================================

# test a loaded python_string method

ashesLoader = TemplatePathLoaderExtended('%stemplates_a' % templates_directory)
ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))

# grab the string and compiled for the next 2 tests
python_string__apples = ashesEnv.load('apples.dust').to_python_string()
python_string__oranges = ashesEnv.load('oranges.dust').to_python_string()
python_function__apples = ashes.compile_python_string(python_string__apples)
python_function__oranges = ashes.compile_python_string(python_string__oranges)

if EXPORT:
    open("%s/apples-python_string.txt" % EXPORTS_DIR, "w").write(python_string__apples)
    open("%s/oranges-python_string.txt" % EXPORTS_DIR, "w").write(python_string__oranges)

if PRINT_SAMPLE:
    print "========================"
    print "python_string__apples = '''", python_string__apples, "'''"
    print "python_string__oranges = '''", python_string__oranges, "'''"
    print "========================"

@utils.timeit
def test_python_string():
    ashesLoader = TemplatePathLoaderExtended('%stemplates_a' % templates_directory)
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    ashesEnv.register(ashesLoader.load_precompiled('apples.dust', source_python_string=python_string__apples),
                      name="apples.dust",
                      )
    ashesEnv.register(ashesLoader.load_precompiled('oranges.dust', source_python_string=python_string__oranges),
                      name="oranges.dust",
                      )
    templated = ashesEnv.render('oranges.dust', {})
    return templated

for i in range(0, ITERATIONS):
    rendered_oranges = test_python_string()

rendered_oranges_python_string = rendered_oranges

if PRINT_SAMPLE:
    print "========================"
    print "Loaded Python String method"
    utils.print_timed()
    print rendered_oranges_python_string
    print "========================"


# ==============================================================================
# ==============================================================================


if PRINT_SAMPLE:
    print "========================"
    print "python_function__apples = '''", python_function__apples, "'''"
    print "python_function__oranges = '''", python_function__oranges, "'''"
    print "========================"


@utils.timeit
def test_python_compiled():
    ashesLoader = TemplatePathLoaderExtended('%stemplates_a' % templates_directory)
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    ashesEnv.register(ashesLoader.load_precompiled('apples.dust', source_python_func=python_function__oranges),
                      name="apples.dust",
                      )
    ashesEnv.register(ashesLoader.load_precompiled('oranges.dust', source_python_func=python_function__apples),
                      name="oranges.dust",
                      )
    templated = ashesEnv.render('oranges.dust', {})
    return templated

for i in range(0, ITERATIONS):
    rendered_oranges = test_python_compiled()

rendered_oranges_python_function = rendered_oranges

if PRINT_SAMPLE:
    print "========================"
    print "Loaded Python Compiled method"
    utils.print_timed()
    print rendered_oranges_python_function
    print "========================"


print "rendered_oranges_baseline        ", hashlib.md5(rendered_oranges_baseline).hexdigest()
print "rendered_oranges_ast             ", hashlib.md5(rendered_oranges_ast).hexdigest()
print "rendered_oranges_python_string   ", hashlib.md5(rendered_oranges_python_string).hexdigest()
print "rendered_oranges_python_function ", hashlib.md5(rendered_oranges_python_function).hexdigest()


if not PRINT_SAMPLE:
    utils.timed_stats()
