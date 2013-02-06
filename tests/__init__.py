from .core import AshesTest
from . import dust_site


def _get_sorted_tests(module):
    tests = [t for t in module.__dict__.values()
             if hasattr(t, 'ast') and issubclass(t, AshesTest)]
    return sorted(tests, key=lambda x: len(x.template or ''))


dust_site_tests = _get_sorted_tests(dust_site)
