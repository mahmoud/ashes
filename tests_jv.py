"""
This is just a quick file to bench test the various ways of loading data


"""

import ashes
import pprint
import tests_jv_utils

# ==============================================================================
# ==============================================================================


ITERATIONS = 1000
PRINT_SAMPLE = False


# ==============================================================================
# ==============================================================================


# test the baseline


@tests_jv_utils.timeit
def test_baseline():
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated


_sample = None
for i in range(0, ITERATIONS):
    test_baseline()


if PRINT_SAMPLE:
    print "========================"
    print "Normal method"
    tests_jv_utils.print_timed()
    print _sample
    print "========================"


# ==============================================================================
# ==============================================================================
# ==============================================================================

# test a loaded ast method

ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
ast__oranges = ashesEnv.generate_ast('oranges.dust')
ast__apples = ashesEnv.generate_ast('apples.dust')


@tests_jv_utils.timeit
def test_ast():
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    ashesEnv.load_template_ast('oranges.dust', ast__oranges)
    ashesEnv.load_template_ast('apples.dust', ast__apples)
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated


_sample = None
for i in range(0, ITERATIONS):
    test_ast()


if PRINT_SAMPLE:
    print "========================"
    print "Loaded AST method"
    tests_jv_utils.print_timed()
    print _sample
    print "========================"


# ==============================================================================
# ==============================================================================
# ==============================================================================

# test a loaded python_string method


ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
python_string__oranges = ashesEnv.generate_python_string('oranges.dust')
python_string__apples = ashesEnv.generate_python_string('apples.dust')
python_function__oranges = ashes.compile_python_string(python_string__oranges)
python_function__apples = ashes.compile_python_string(python_string__apples)


@tests_jv_utils.timeit
def test_python_string():
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    _loaded = ashesEnv.load_template_python_string('oranges.dust', python_string__oranges)
    _loaded = ashesEnv.load_template_python_string('apples.dust', python_string__apples)
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated


_sample = None
for i in range(0, ITERATIONS):
    test_python_string()


if PRINT_SAMPLE:
    print "========================"
    print "Loaded Python String method"
    tests_jv_utils.print_timed()
    print _sample
    print "========================"


@tests_jv_utils.timeit
def test_python_compiled():
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    _loaded = ashesEnv.load_template_python_compiled('oranges.dust', python_function__oranges)
    _loaded = ashesEnv.load_template_python_compiled('apples.dust', python_function__apples)
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated


_sample = None
for i in range(0, ITERATIONS):
    test_python_compiled()


if PRINT_SAMPLE:
    print "========================"
    print "Loaded Python Compiled method"
    tests_jv_utils.print_timed()
    print _sample
    print "========================"


if not PRINT_SAMPLE:
    tests_jv_utils.timed_stats()
