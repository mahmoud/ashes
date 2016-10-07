"""
These are example loads for use in tests
"""

# stdlib
import os
import codecs
import ashes


class TemplatePathLoaderExtended(ashes.TemplatePathLoader):
    """extends the ashes TemplatePathLoader"""
    def load_precompiled(
        self,
        template_name,
        source=None,
        source_ast=None,
        source_python_string=None,
        source_python_func=None,
    ):
        template = ashes.Template(template_name,
                                  source,
                                  source_ast=source_ast,
                                  source_python_string=source_python_string,
                                  source_python_func=source_python_func,
                                  )
        return template


class TemplatesLoader(object):
    """Base Class; used to load template requests from the cache"""

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

    def load_all(self):
        """
        DEMO
        our load_all will just create template objects from the _template_source_dust files
        """
        for _template_name in self._template_source_dust.keys():
            if _template_name not in self._template_objects:
                print "_template_name", _template_name
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

            # stash local            
            self._template_ast[_template_name] = _ast
            self._template_python_string[_template_name] = _python_string

            # stash payload
            payload[_template_name] = {'ast': _ast,
                                       'python_string': _python_string,
                                       }
        return payload

    def status(self):
        """prints a status object"""
        status_obj = {'_template_source_dust': {'info': "loaded dust source files",
                                                'items': self._template_source_dust.keys(),
                                                },
                      '_template_objects': {'info': 'compiled ashes.Template objects',
                                            'items': self._template_objects.keys(),
                                            },
                      '_template_ast': {'info': 'compiled ashes.Template ast (cacheable)',
                                        'items': self._template_ast.keys(),
                                        },
                      '_template_python_string': {'info': 'compiled ashes.Template python strings (cacheable)',
                                                  'items': self._template_python_string.keys(),
                                                  },
                      }
        return status_obj


class TemplatesLoaderLazy(TemplatesLoader):
    _generated_cacheable = None

    def __init__(self, directory=None):
        """
        DEMO
        """
        TemplatesLoader.__init__(self, directory=None)
        self._directory = directory
        
        # we'll stash changes in here
        self._generated_cacheable = {}

    def load(self, template_name, env=None):
        """
        DEMO
        we subclass the TemplatesLoader and try to initialize as we go along
        """
        # did we already compile this into a template object?
        if template_name in self._template_objects:
            return self._template_objects[template_name]

        # okay, let's see if we can load it
        if self._directory:
            directory = os.path.normpath(self._directory)
            try:
                filepath = os.path.join(directory, template_name)
                template_source = codecs.open(filepath, 'r', 'utf-8').read() 
                _templateObj = ashes.Template(template_name,
                                              template_source
                                              )
                # stash the object
                self._template_objects[template_name] = _templateObj
                
                # generate cacheable
                _ast = _templateObj.to_ast()
                _python_string = _templateObj.to_python_string()

                # stash local            
                self._template_ast[template_name] = _ast
                self._template_python_string[template_name] = _python_string
                
                # note our changes
                self._generated_cacheable[template_name] = {'ast': _ast,
                                                            'python_string': _python_string,
                                                            }
                return _templateObj
            except:
                raise

        raise ashes.TemplateNotFound(template_name)

    def generated_cacheable(self):
        """access our private storage if anything changed"""
        return self._generated_cacheable