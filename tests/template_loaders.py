# -*- coding: utf-8 -*-

# stdlib
import json
import os
import codecs
import unittest

from .core import AshesTestExtended
import ashes

from . import utils


# ==============================================================================



class TestChertTemplates(unittest.TestCase):

    _ChertData = None

    def setUp(self):
        # sets up the global chert object
        if utils.ChertDefaults is None:
            utils.ChertDefaults = utils._ChertDefaults()
        self._ChertData = utils.ChertDefaults

    def test_cachable_templates(self):
        # can we cache the templates in all these ways?
        # this just ensures the renderer can be built
        render_fails = {}
        for _source_text in (
            'all', 
            'ast',
            'python_string',
            'python_code',
        ):
            # build a new cacheable templates...
            ashesLoader = utils.TemplatesLoader()
            ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
            ashesLoader.load_from_cacheable(self._ChertData.cacheable_templates_typed[_source_text])

            for (fname, fdata) in self._ChertData.chert_data.items():
                rendered = ashesEnv.render(fname, fdata)
                if rendered != self._ChertData.renders_expected[fname]:
                    if _source_text not in render_fails:
                        render_fails[_source_text] = {}
                    render_fails[_source_text][fname] = rendered
        self.assertEqual(len(render_fails.keys()), 0)


    def test_Template_tofrom_ast(self):
        ashesEnvSrc = ashes.AshesEnv(paths=[utils._chert_dir,])
        ashesEnvDest = ashes.AshesEnv()
        template_base = ashes.Template('base.html',  self._ChertData.chert_data_alt['base.html'])
        ashesEnvDest.register(template_base, 'base.html')
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_ast = ashesEnvSrc.load(fname).to_ast()
            template2_object = ashes.Template(fname,
                                              None,
                                              source_ast=source_ast,
                                              )
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_string(self):
        ashesEnvSrc = ashes.AshesEnv(paths=[utils._chert_dir,])
        ashesEnvDest = ashes.AshesEnv()
        template_base = ashes.Template('base.html',  self._ChertData.chert_data_alt['base.html'])
        ashesEnvDest.register(template_base, 'base.html')
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_string = ashesEnvSrc.load(fname).to_python_string()
            template2_object = ashes.Template(fname,
                                              None,
                                              source_python_string=source_python_string,
                                              )
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_code(self):
        ashesEnvSrc = ashes.AshesEnv(paths=[utils._chert_dir,])
        ashesEnvDest = ashes.AshesEnv()
        template_base = ashes.Template('base.html',  self._ChertData.chert_data_alt['base.html'])
        ashesEnvDest.register(template_base, 'base.html')
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_code = ashesEnvSrc.load(fname).to_python_code()
            template2_object = ashes.Template(fname,
                                              None,
                                              source_python_code=source_python_code,
                                              )
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_func(self):
        ashesEnvSrc = ashes.AshesEnv(paths=[utils._chert_dir,])
        ashesEnvDest = ashes.AshesEnv()
        template_base = ashes.Template('base.html',  self._ChertData.chert_data_alt['base.html'])
        ashesEnvDest.register(template_base, 'base.html')
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_func = ashesEnvSrc.load(fname).to_python_func()
            template2_object = ashes.Template(fname,
                                              None,
                                              source_python_func=source_python_func,
                                              )
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]
