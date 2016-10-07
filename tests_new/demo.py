"""
This is just a quick file to bench test the various ways of loading data


"""

# stdlib
import os
import pprint
import timeit

# local
import tests_compiled_utils as utils
from tests_compiled_loaders import TemplatesLoader, TemplatesLoaderLazy

# ==============================================================================
# ==============================================================================

import ashes

# ==============================================================================
# ==============================================================================

templates_directory = '../tests/'

# ==============================================================================
# ==============================================================================


# test a loaded python_string method
ashesLoader = TemplatesLoader('%stemplates_a' % templates_directory)
ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))

# peep inside!
# pprint.pprint(ashesLoader.status())

# grab the string and compiled for the next 2 tests
python_string__apples = ashesEnv.load('apples.dust').to_python_string()
# peep inside!
# pprint.pprint(ashesLoader.status())

cacheable_templates = ashesLoader.generate_all_cacheable()
# peep inside!
# pprint.pprint(ashesLoader.status())

# create a new loader, without the files
ashesLoaderAlt = TemplatesLoader()
ashesEnvAlt = ashes.AshesEnv(loaders=(ashesLoaderAlt, ))

# peep inside!
# pprint.pprint(ashesLoaderAlt.status())

# load it
ashesLoaderAlt.load_from_cacheable(cacheable_templates)

# peep inside!
# pprint.pprint(ashesLoaderAlt.status())

# hey does it work?
templated_a = ashesEnvAlt.render('oranges.dust', {})
templated_b = ashesEnv.render('oranges.dust', {})
print "(templated_a == templated_b) = ", (templated_a == templated_b)

# okay, try lazyloading!
ashesLoaderLazy = TemplatesLoaderLazy('%stemplates_a' % templates_directory)
ashesEnvLazy = ashes.AshesEnv(loaders=(ashesLoaderLazy, ))
templated_a = ashesEnvLazy.render('oranges.dust', {})
print "(templated_a == templated_b) = ", (templated_a == templated_b)


# peek inside?
# print ashesLoaderLazy.generated_cacheable()

