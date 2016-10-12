# -*- coding: utf-8 -*-

# stdlib
import unittest
import os

# package
import ashes

# local
from . import utils


# ==============================================================================


class TestChertTemplates(unittest.TestCase):

    _ChertData = None

    def setUp(self):
        # sets up the global chert object
        if utils.ChertDefaults is None:
            utils.ChertDefaults = utils._ChertDefaults()
        self._ChertData = utils.ChertDefaults

    def _generate_envs_tofrom(self):
        """
        this generates ashes environments for the to/from tests
        """
        ashesEnvSrc = ashes.AshesEnv(paths=[utils._chert_dir, ])
        ashesEnvDest = ashes.AshesEnv()
        self._ChertData.register_alt_templates(ashesEnvDest)
        return (ashesEnvSrc, ashesEnvDest)

    def test_cachable_templates(self):
        """
        can we cache the templates in all these ways?
        this just ensures the renderer can be built
        """
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
            ashesLoader.load_from_cacheable(
                self._ChertData.cacheable_templates_typed[_source_text]
            )
            for (fname, fdata) in self._ChertData.chert_data.items():
                rendered = ashesEnv.render(fname, fdata)
                if rendered != self._ChertData.renders_expected[fname]:
                    if _source_text not in render_fails:
                        render_fails[_source_text] = {}
                    render_fails[_source_text][fname] = rendered
        self.assertEqual(len(render_fails.keys()), 0)

    def test_Template_tofrom_ast(self):
        """
        tests a roundtrip from AST
        """
        (ashesEnvSrc, ashesEnvDest) = self._generate_envs_tofrom()
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_ast = ashesEnvSrc.load(fname).to_ast()
            template2_object = ashes.Template.from_ast(source_ast)
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_string(self):
        """
        tests a roundtrip from Python string
        """
        (ashesEnvSrc, ashesEnvDest) = self._generate_envs_tofrom()
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_string = ashesEnvSrc.load(fname).to_python_string()
            template2_object = ashes.Template.from_python_string(source_python_string)
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_code(self):
        """
        tests a roundtrip from Python code objects
        """
        (ashesEnvSrc, ashesEnvDest) = self._generate_envs_tofrom()
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_code = ashesEnvSrc.load(fname).to_python_code()
            template2_object = ashes.Template.from_python_code(source_python_code)
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]

    def test_Template_tofrom_python_func(self):
        """
        tests a roundtrip from Python functions
        """
        (ashesEnvSrc, ashesEnvDest) = self._generate_envs_tofrom()
        for (fname, fdata) in self._ChertData.chert_data.items():
            source_python_func = ashesEnvSrc.load(fname).to_python_func()
            template2_object = ashes.Template.from_python_func(source_python_func)
            ashesEnvDest.register(template2_object, fname)
            rendered2 = ashesEnvDest.render(fname, fdata)
            assert rendered2 == self._ChertData.renders_expected[fname]


class TestApiFunctions(unittest.TestCase):

    _SimpleFruitData = None

    def setUp(self):
        # sets up the global chert object
        if utils.SimpleFruitDefaults is None:
            utils.SimpleFruitDefaults = utils._SimpleFruitDefaults()
        self._SimpleFruitData = utils.SimpleFruitDefaults

    def test_AshesEnv_path(self):
        """this tests an ashesEnv initialized with a path"""
        ashesEnv = ashes.AshesEnv(paths=self._SimpleFruitData.directory)
        for _fruit in self._SimpleFruitData.template_source.keys():
            _rendered = ashesEnv.render(_fruit, {})
            self.assertEquals(_rendered, self._SimpleFruitData.renders_expected[_fruit])

    def test_TemplatePathLoader(self):
        """this tests an ashesEnv initialized with a `loaders=ashes.TemplatePathLoader()`"""
        ashesLoader = ashes.TemplatePathLoader(root_path=self._SimpleFruitData.directory)
        ashesEnv = ashes.AshesEnv(loaders=(ashesLoader, ))
        for _fruit in self._SimpleFruitData.template_source.keys():
            _rendered = ashesEnv.render(_fruit, {})
            self.assertEquals(_rendered, self._SimpleFruitData.renders_expected[_fruit])

    def test_template_init_source(self):
        """
        this tests a template can be initialized from source.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                _template = ashes.Template(_fruit, self._SimpleFruitData.template_source[_fruit])
                _rendered = _template.render({})
                self.assertEquals(_rendered, self._SimpleFruitData.renders_expected[_fruit])

    def test_template_init_source_file(self):
        """
        this tests a template can be initialized from a source_file argument.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                _source_file = os.path.join(self._SimpleFruitData.directory, _fruit)
                _template = ashes.Template(_fruit, None, source_file=_source_file)
                _rendered = _template.render({})
                self.assertEquals(_rendered, self._SimpleFruitData.renders_expected[_fruit])

    def _helper_test_template_init__args(self, fruit, source_payload=None, source_classmethod=None):
        """helper class for _helper_test_template_init__args_* tests"""
        source_data = self._SimpleFruitData.compiled_template_data[fruit][source_payload]
        
        # can it render via classmethod?
        _template = source_classmethod(source_data)
        _rendered = _template.render({})
        self.assertEquals(_rendered, self._SimpleFruitData.renders_expected[fruit])

    def test_template_init_args_ast(self):
        """
        this tests a template can be initialized from a source_file argument.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                self._helper_test_template_init__args(_fruit, source_payload='ast', source_classmethod=ashes.Template.from_ast)

    def test_template_init_args_python_string(self):
        """
        this tests a template can be initialized from a source_file argument.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                self._helper_test_template_init__args(_fruit, source_payload='python_string', source_classmethod=ashes.Template.from_python_string)

    def test_template_init_args_python_code(self):
        """
        this tests a template can be initialized from a source_file argument.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                self._helper_test_template_init__args(_fruit, source_payload='python_code', source_classmethod=ashes.Template.from_python_code)

    def test_template_init_args_python_func(self):
        """
        this tests a template can be initialized from a source_file argument.
        this does not test the templates with dependencies, as they must be executed with a loader
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            if _fruit not in self._SimpleFruitData.template_dependencies:
                self._helper_test_template_init__args(_fruit, source_payload='python_func', source_classmethod=ashes.Template.from_python_func)

    def test_loaded_template_conversion(self):
        """
        there had been an earlier uncaught edgecase, in which a loaded template did not generate the right data
        """
        ashesEnv = ashes.AshesEnv(paths=self._SimpleFruitData.directory)
        for _fruit in self._SimpleFruitData.template_source.keys():
            _template = ashesEnv.load(_fruit)

            _as_ast = _template.to_ast()
            self.assertEquals(_as_ast, self._SimpleFruitData.compiled_template_data[_fruit]['ast'])

            _as_python_string = _template.to_python_string()
            self.assertEquals(_as_python_string, self._SimpleFruitData.compiled_template_data[_fruit]['python_string'])

            _as_python_code = _template.to_python_code()
            self.assertEquals(_as_python_code, self._SimpleFruitData.compiled_template_data[_fruit]['python_code'])

            # this will never equate, but it must run!
            _as_python_func = _template.to_python_func()

    def test_alt_template_conversion(self):
        """
        if a template has been initialized from cachable version, what happens if we try to convert it?
        
        we should raise an TemplateConversionException
        
        """
        for _fruit in self._SimpleFruitData.template_source.keys():
            _template = ashes.Template.from_ast(self._SimpleFruitData.compiled_template_data[_fruit]['ast'], name=_fruit)
            self.assertRaises(ashes.TemplateConversionException, _template.to_ast)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_string)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_code)
            # self.assertRaises(ashes.TemplateConversionException, _template.to_python_func)  # allowed

            _template = ashes.Template.from_python_string(self._SimpleFruitData.compiled_template_data[_fruit]['python_string'], name=_fruit)
            self.assertRaises(ashes.TemplateConversionException, _template.to_ast)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_string)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_code)
            # self.assertRaises(ashes.TemplateConversionException, _template.to_python_func)  # allowed

            _template = ashes.Template.from_python_code(self._SimpleFruitData.compiled_template_data[_fruit]['python_code'], name=_fruit)
            self.assertRaises(ashes.TemplateConversionException, _template.to_ast)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_string)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_code)
            # self.assertRaises(ashes.TemplateConversionException, _template.to_python_func)  # allowed

            _template = ashes.Template.from_python_func(self._SimpleFruitData.compiled_template_data[_fruit]['python_func'], name=_fruit)
            self.assertRaises(ashes.TemplateConversionException, _template.to_ast)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_string)
            self.assertRaises(ashes.TemplateConversionException, _template.to_python_code)
            # self.assertRaises(ashes.TemplateConversionException, _template.to_python_func)  # allowed
            
            
            
