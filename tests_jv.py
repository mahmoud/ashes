import ashes
import pprint


# ==============================================================================
# ==============================================================================


ITERATIONS = 1000
PRINT_SAMPLE = True


# ==============================================================================
# ==============================================================================



# test the baseline

_sample = None
for i in range(0, ITERATIONS):
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated
print "========================"
print "Normal method"
ashes.print_timed()
ashes.timeditems = {}
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

_sample = None
for i in range(0, ITERATIONS):
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    ashesEnv.load_template_ast('oranges.dust', ast__oranges)
    ashesEnv.load_template_ast('apples.dust', ast__apples)
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated
print "========================"
print "Loaded AST method"
ashes.print_timed()
ashes.timeditems = {}
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

_sample = None
for i in range(0, ITERATIONS):
    ashesLoader = ashes.TemplatePathLoader('tests_jv-templates')
    ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
    _loaded = ashesEnv.load_template_python_compiled('oranges.dust', python_function__oranges)
    _loaded = ashesEnv.load_template_python_compiled('apples.dust', python_function__apples)
    templated = ashesEnv.render('oranges.dust', {})
    if PRINT_SAMPLE and i == 0:
        _sample = templated
print "========================"
print "Loaded Python String method"
ashes.print_timed()
ashes.timeditems = {}
print _sample
print "========================"
