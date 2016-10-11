# -*- coding: utf-8 -*-

# stdlib
import unittest
import marshal

import timeit
import time

import ashes

from . import utils

__all__ = ['bench_render_a', 'bench_cacheable_templates', ]

# ==============================================================================


def bench_render_a():
    """
    this bench is designed as a baseline for performance comparisons when
    adjusting the code
    """
    print "running benchmarks: bench_render_a..."
    if utils.ChertDefaults is None:
        utils.ChertDefaults = utils._ChertDefaults()

    def test_baseline_chert():
        """
        test_baseline_chert
        this just runs though all the chert templates using a default `TemplatePathLoader`
        """
        renders = {}
        _ashesLoader = ashes.TemplatePathLoader(utils._chert_dir)
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    timed = {}
    ranged = range(0, 100)
    timed["baseline_chert"] = []
    for i in ranged:
        t_start = time.time()
        test_baseline_chert()
        t_fin = time.time()
        timed["baseline_chert"] .append(t_fin - t_start)
    utils.print_timed(timed)


def bench_cacheable_templates():
    """
    This just runs a few strategies of template generation to compare against 
    one another
    """
    print "running benchmarks: bench_cacheable_templates..."

    if utils.ChertDefaults is None:
        utils.ChertDefaults = utils._ChertDefaults()

    ashesDataLoader = utils.TemplatePathLoaderExtended(utils._chert_dir)
    ashesEnvLoader = ashes.AshesEnv(loaders=(ashesDataLoader, ))

    templateData = {'ast': {},
                    'python_string': {},
                    'python_code': {},
                    'python_code-marshal': {},
                    'python_func': {},
                    }
    for (fname, fdata) in utils.ChertDefaults.chert_data.items():
        templateData['ast'][fname] = ashesEnvLoader.load(fname).to_ast()
        templateData['python_string'][fname] = ashesEnvLoader.load(fname).to_python_string()
        templateData['python_code'][fname] = ashes.python_string_to_code(templateData['python_string'][fname])
        templateData['python_code-marshal'][fname] = marshal.dumps(templateData['python_code'][fname])
        templateData['python_func'][fname] = ashes.python_string_to_function(templateData['python_string'][fname])

    # generate the inherited templates
    for (fname, fdata) in utils.ChertDefaults.chert_files_html_alt.items():
        template = ashes.Template(fname, utils.ChertDefaults.chert_files_html_alt[fname])
        ashesEnvLoader.register(template, fname)
        templateData['ast'][fname] = ashesEnvLoader.load(fname).to_ast()
        templateData['python_string'][fname] = ashesEnvLoader.load(fname).to_python_string()
        templateData['python_code'][fname] = ashes.python_string_to_code(templateData['python_string'][fname])
        templateData['python_code-marshal'][fname] = marshal.dumps(templateData['python_code'][fname])
        templateData['python_func'][fname] = ashes.python_string_to_function(templateData['python_string'][fname])

    def test_baseline():
        """
        test_baseline
        this should be the longest and the normal ashes behavior
        """
        renders = {}
        _ashesLoader = ashes.TemplatePathLoader(utils._chert_dir)
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    def test_ast():
        _ashesLoader = utils.TemplatePathLoaderExtended()
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        renders = {}
        for (fname, fdata) in templateData['ast'].items():
            _ashesEnv.register(_ashesLoader.load_precompiled(fname, source_ast=fdata),
                               name=fname,
                               )
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    def test_python_string():
        _ashesLoader = utils.TemplatePathLoaderExtended()
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        renders = {}
        for (fname, fdata) in templateData['python_string'].items():
            _ashesEnv.register(_ashesLoader.load_precompiled(fname, source_python_string=fdata),
                               name=fname,
                               )
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    def test_python_code():
        _ashesLoader = utils.TemplatePathLoaderExtended()
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        renders = {}
        for (fname, fdata) in templateData['python_code-marshal'].items():
            fdata = marshal.loads(fdata)
            _ashesEnv.register(_ashesLoader.load_precompiled(fname, source_python_code=fdata),
                               name=fname,
                               )
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    def test_python_func():
        _ashesLoader = utils.TemplatePathLoaderExtended()
        _ashesEnv = ashes.AshesEnv(loaders=(_ashesLoader, ))
        renders = {}
        for (fname, fdata) in templateData['python_func'].items():
            _ashesEnv.register(_ashesLoader.load_precompiled(fname, source_python_func=fdata),
                               name=fname,
                               )
        for (fname, fdata) in utils.ChertDefaults.chert_data.items():
            rendered = _ashesEnv.render(fname, fdata)
            renders[fname] = fdata

    # test_baseline()
    # test_ast()
    # test_python_string()
    # test_python_code()
    # test_python_func()

    timed = {}
    ranged = range(0, 100)
    for t in (('test_baseline', test_baseline),
              ('test_ast', test_ast),
              ('test_python_string', test_python_string),
              ('test_python_code', test_python_code),
              ('test_python_func', test_python_func),
              ):
        print(" .%s" % t[0])
        timed[t[0]] = []
        for i in ranged:
            t_start = time.time()
            t[1]()
            t_fin = time.time()
            timed[t[0]].append(t_fin - t_start)
    utils.print_timed(timed)
