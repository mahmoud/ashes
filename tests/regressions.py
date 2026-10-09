# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest

from ashes import Template

from .core import AshesTest


class unicode_url(AshesTest):
    "Reported by @ambar"
    template = '{q|u}'
    json_context = '{"q": "中文"}'
    rendered = '%E4%B8%AD%E6%96%87'


class FalsyComparisonTests(unittest.TestCase):
    def test_zero_key(self):
        template = Template('zero', '{@eq key=value value=0}yes{:else}no{/eq}')
        self.assertEqual(template.render({'value': 0}), 'yes')

    def test_false_key(self):
        template = Template('false', '{@eq key=value value=other}yes{:else}no{/eq}')
        self.assertEqual(template.render({'value': False, 'other': False}), 'yes')

    def test_empty_string_key(self):
        template = Template('empty', '{@eq key=value value=""}yes{:else}no{/eq}')
        self.assertEqual(template.render({'value': ''}), 'yes')

    def test_explicit_zero_overrides_select_key(self):
        template = Template('selected', '{@select key=1}{@eq key=value value=0}yes{/eq}{/select}')
        self.assertEqual(template.render({'value': 0}), 'yes')
