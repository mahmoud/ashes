# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from ashes import Template, escape_uri_component

from .core import AshesTest


class unicode_url(AshesTest):
    "Reported by @ambar"
    template = '{q|u}'
    json_context = '{"q": "中文"}'
    rendered = '%E4%B8%AD%E6%96%87'


class URIComponentTests(unittest.TestCase):
    def test_component_delimiters(self):
        self.assertEqual(escape_uri_component('a:b#c'), 'a%3Ab%23c')

    def test_component_filter_in_template(self):
        template = Template('query', '/find?q={value|uc}')
        self.assertEqual(template.render({'value': 'a:b#c'}), '/find?q=a%3Ab%23c')

    def test_existing_escapes(self):
        self.assertEqual(escape_uri_component('a/b?c=d&e'), 'a%2Fb%3Fc%3Dd%26e')
