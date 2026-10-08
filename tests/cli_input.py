from __future__ import unicode_literals

import os
import shutil
import subprocess
import sys
import tempfile
import unittest

import ashes


class CLIInputTests(unittest.TestCase):
    def render(self, model_args, input_data, expected):
        directory = tempfile.mkdtemp()
        try:
            path = os.path.join(directory, 'output.txt')
            process = subprocess.Popen(
                [sys.executable, ashes.__file__, '-T', 'Hello, {name}!', '-o', path] + model_args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = process.communicate(input_data)
            self.assertEqual(0, process.returncode, error)
            with open(path, 'rb') as result:
                self.assertEqual(expected, result.read())
        finally:
            shutil.rmtree(directory)

    def test_model_defaults_to_stdin(self):
        self.render([], b'{"name": "stdin"}', b'Hello, stdin!')

    def test_explicit_stdin(self):
        self.render(['-m', '-'], b'{"name": "explicit"}', b'Hello, explicit!')

    def test_literal_model_takes_precedence(self):
        self.render(['-M', '{"name": "literal"}'], b'not json', b'Hello, literal!')

    def test_explicit_model_file_takes_precedence(self):
        directory = tempfile.mkdtemp()
        try:
            path = os.path.join(directory, 'model.json')
            with open(path, 'w') as model:
                model.write('{"name": "file"}')
            self.render(['-m', path], b'not json', b'Hello, file!')
        finally:
            shutil.rmtree(directory)
