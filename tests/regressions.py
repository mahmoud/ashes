# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .core import AshesTest


class unicode_url(AshesTest):
    "Reported by @ambar"
    template = '{q|u}'
    json_context = '{"q": "中文"}'
    rendered = '%E4%B8%AD%E6%96%87'
