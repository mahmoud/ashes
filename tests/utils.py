# -*- coding: utf-8 -*-
"""
These utilities are designed for incorporation into tests
"""

# stdlib
import os
import codecs
import json
import time
import operator


import ashes


# ==============================================================================

# we'll store a global value in here
ChertDefaults = None
_chert_dir = '%s/templates_chert' % os.path.dirname(os.path.realpath(__file__))


class _ChertDefaults(object):
    """
    Generate an object to stash Chert Data
    TODO - we should load/stash/compare the final renders
    """
    
    # this will become a dict mapping the html filename to a dict to render (from json)
    chert_data = None

    # map the rendered data for comparison
    renders_expected = None
    cacheable_templates_typed = None
    
    def __init__(self):

        # Globals Setup
        # load all the chert templates
        _chert_files_all = os.listdir(_chert_dir)

        # we only want the .html templates
        _chert_files_html = [i for i in _chert_files_all if i[-5:] == '.html']
        # we only want the .html templates
        _chert_files_html_json = [i for i in _chert_files_all if i[-10:] == '.html.json']

        # load  the json data
        chert_data = {}
        for f in _chert_files_html:
            f_json = f + '.json'
            if f_json in _chert_files_html_json:
                _fpath = os.path.join(_chert_dir, f_json)
                json_data = codecs.open(_fpath, 'r', 'utf-8').read()
                chert_data[f] = json.loads(json_data)
        self.chert_data = chert_data

        chert_data_alt = {}
        for _fname in ('base.html', ):
            _fpath = os.path.join(_chert_dir, _fname)
            chert_data_alt = {_fname: codecs.open(_fpath, 'r', 'utf-8').read(), }
        self.chert_data_alt = chert_data_alt

        # okay, let's generate the expected data...
        renders_expected = {}
        ashesEnv = ashes.AshesEnv(paths=[_chert_dir,], )
        for (fname, fdata) in chert_data.items():
            rendered = ashesEnv.render(fname, fdata)
            renders_expected[fname] = rendered
        self.renders_expected = renders_expected
    
        # and generate some cacheable templates
        ashesPreloader = TemplatesLoader(directory=_chert_dir)
        cacheable_templates = ashesPreloader.generate_all_cacheable()
        self.cacheable_templates = cacheable_templates

        # make an isolated version for testing...
        cacheable_templates_typed = {'all': {},
                                     'ast': {},
                                     'python_string': {},
                                     'python_code': {},
                                     }
        for (k, payload) in cacheable_templates.items():
            cacheable_templates_typed['all'][k] = payload
            cacheable_templates_typed['ast'][k] = {'ast': payload['ast'], }
            cacheable_templates_typed['python_string'][k] = {'python_string': payload['python_string'], }
            cacheable_templates_typed['python_code'][k] = {'python_code': payload['python_code'], }
        self.cacheable_templates_typed = cacheable_templates_typed

# ==============================================================================


class TemplatesLoader(object):
    """Example Template Loader Class; used to load template requests from a cache"""

    # stash the directory
    _directory = None

    # cache of template objects
    _template_objects = None

    # cache of dust data
    _template_source_dust = None

    # cache for cacheable data
    _template_ast = {}
    _template_python_string = {}

    def __init__(self, directory=None):
        """
        DEMO
        when we start up, we'll load the template directory contents into the object class
        we won't generate any template data, just load the files
        
        if directory is not passed in, don't preload!
        """
        self._directory = directory
        # initialize placeholder for compiled templates into here
        self._template_objects = {}

        # preload all the raw template data 
        self._template_source_dust = {}
        if directory:
            directory = os.path.normpath(directory)
            files = [i for i in os.listdir(os.path.normpath(directory)) if i[-5:] in ('.dust', '.html')]
            fpaths = {f: os.path.join(directory, f) for f in files}
            fdata = {f: codecs.open(fpaths[f], 'r', 'utf-8').read() for f in files}
            self._template_source_dust = fdata

        # initialize
        self._template_ast = {}
        self._template_python_string = {}
        self._template_python_code = {}

    def load_all(self):
        """
        DEMO
        our load_all will just create template objects from the _template_source_dust files
        """
        for _template_name in self._template_source_dust.keys():
            if _template_name not in self._template_objects:
                self._template_objects[_template_name] = ashes.Template(_template_name,
                                                                        self._template_source_dust[_template_name]
                                                                        )

    def load(self, template_name, env=None):
        """
        DEMO
        our load_all will just create template objects from the _template_source_dust files
        """
        # did we already compile this into a template object?
        if template_name in self._template_objects:
            return self._template_objects[template_name]

        # maybe we have the source?
        if template_name in self._template_source_dust:
            # build a template
            _templateObj = ashes.Template(template_name,
                                          self._template_source_dust[template_name]
                                          )

            # stash the source
            self._template_objects[template_name] = _templateObj

            # return the template
            return _templateObj

        raise ashes.TemplateNotFound(template_name)


    def load_from_cacheable(self, templates_cache):
        """
        DEMO
        templates_cache is generated via `generate_all_cacheable`
        """
        for (_template_name, payload) in templates_cache.items():
            self._template_objects[_template_name] = ashes.Template(_template_name,
                                                                    None,
                                                                    source_ast=payload.get('ast'),
                                                                    source_python_string=payload.get('python_string'),
                                                                    source_python_code=payload.get('python_code'),
                                                                    )

    def generate_all_cacheable(self):
        """
        DEMO
        this will generate a payload that can be loaded via `load_from_cacheable`
        """
        # load EVERYTHING first
        self.load_all()
        payload = {}
        for (_template_name, _templateObj) in self._template_objects.items():
            # generate cacheable
            _ast = _templateObj.to_ast()
            _python_string = _templateObj.to_python_string()
            _python_code = _templateObj.to_python_code()

            # stash local            
            self._template_ast[_template_name] = _ast
            self._template_python_string[_template_name] = _python_string
            self._template_python_code[_template_name] = _python_code

            # stash payload
            payload[_template_name] = {'ast': _ast,
                                       'python_string': _python_string,
                                       'python_code': _python_code,
                                       }
        return payload

    def status(self):
        """prints a status object"""
        status_obj = {'template_source_dust': {'info': "loaded dust source files",
                                               'items': self._template_source_dust.keys(),
                                               },
                      'template_objects': {'info': 'compiled ashes.Template objects',
                                           'items': self._template_objects.keys(),
                                           },
                      'template_ast': {'info': 'compiled ashes.Template ast (cacheable)',
                                       'items': self._template_ast.keys(),
                                       },
                      'template_python_string': {'info': 'compiled ashes.Template python strings (cacheable)',
                                                 'items': self._template_python_string.keys(),
                                                 },
                      'template_python_code': {'info': 'compiled ashes.Template python codes (cacheable)',
                                               'items': self._template_python_code.keys(),
                                               },
                      }
        return status_obj



class TemplatePathLoaderExtended(ashes.TemplatePathLoader):
    """extends the ashes TemplatePathLoader"""
    _templates_loaded = None
    
    def __init__(self, directory=''):
        ashes.TemplatePathLoader.__init__(self, directory)
        self._templates_loaded = {}

    def load_precompiled(
        self,
        template_name,
        source=None,
        source_ast=None,
        source_python_string=None,
        source_python_code=None,
        source_python_func=None,
    ):
        template = ashes.Template(template_name,
                                  source,
                                  source_ast=source_ast,
                                  source_python_string=source_python_string,
                                  source_python_code=source_python_code,
                                  source_python_func=source_python_func,
                                  )
        return template


    def load(self, template_name, env=None):
        if template_name in self._templates_loaded:
            template_object = self._templates_loaded[template_name]
        else:
            template_object = ashes.TemplatePathLoader.load(self, template_name, env=env)
            self.register_template(template_name, template_object)
        return template_object
        
    def register_template(self, template_name, template_object):
        self._templates_loaded[template_name] = template_object

    def register_template_render_func(self, template_name, source_python_func):
        template_object = ashes.Template(template_name,
                                         None,
                                         source_python_func=source_python_func,
                                         )
        self.register_template(template_name, template_object)
        return template_object


# ==============================================================================


def print_timed(timeditems):
    """
    displays timing statisics
    """
    data = {}
    for k in timeditems.keys():
        total = sum(timeditems[k])
        sample_size = len(timeditems[k])
        data[k] = {
            'name': k,
            'total': total,
            'average': float(total) / sample_size,
            'sample_size': sample_size,
        }
    data_2 = sorted(data.values(), key=operator.itemgetter('total'))
    baseline = data_2[-1]
    template = "{0:25} | {1:25} | {2:25} | {3:25} | {4:25}"  # column widths: 8, 10, 15, 7, 10
    print template.format("test", "total", "average", "sample_size", "baseline")
    print template.format("----", "-----", "-------", "-----------", "--------")
    for idx, i in enumerate(data_2):
        baseline_shift = (i['total'] / baseline['total'])
        print template.format(i['name'],
                              "{:12.8f}".format(i['total']),
                              "{:12.8f}".format(i['average']),
                              i['sample_size'],
                              "{:.4%}".format(baseline_shift)
                              )
