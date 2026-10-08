# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import io
import json
import os
import subprocess
import sys
import unittest

import ashes


class CLIOutputTests(unittest.TestCase):
    def render(self, text, encoding='utf-8'):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'ascii'
        process = subprocess.Popen(
            [sys.executable, ashes.__file__, '--no-filter', '-T', '{text}',
             '-M', json.dumps({'text': text}), '--output-encoding', encoding],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        output, error = process.communicate()
        self.assertEqual(0, process.returncode, error)
        self.assertEqual(text.encode(encoding), output)

    def test_stdout_preserves_whitespace(self):
        self.render('hello\n\t"world"')

    def test_stdout_preserves_empty_output(self):
        self.render('')

    def test_stdout_uses_utf8(self):
        self.render('caf\u00e9')

    def test_stdout_uses_requested_encoding(self):
        self.render('caf\u00e9', 'latin-1')
        self.render('caf\u00e9', 'utf-16-le')

    def test_text_only_stdout(self):
        output = io.StringIO()
        original = sys.stdout
        try:
            sys.stdout = output
            ashes._simple_render(
                template_path=None, template_literal='{text}', env_path_list=[],
                model_path=None, model_literal=json.dumps({'text': 'caf\u00e9'}),
                trim_whitespace=False, filter='h', no_filter=True,
                output_path='-', output_encoding='utf-8', verbose=False)
        finally:
            sys.stdout = original
        self.assertEqual('caf\u00e9', output.getvalue())
