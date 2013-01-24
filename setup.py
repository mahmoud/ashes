# -*- coding: utf-8 -*-
"""
dust.py provides a Python implementation of the dust_ templating
language. It is a fork of dust-py_.

.. _dust: http://akdubya.github.com/dustjs/
.. _dust-py: https://code.google.com/p/dust-py/

"""
from setuptools import setup


setup(
    name='dust.py',
    version='0.4.0',
    license='MIT',
    author='Mahmoud Hashemi',
    author_email='makuro@gmail.com',
    url='https://github.com/mahmoud/dust.py',
    description='Dust templating for Python',
    long_description=__doc__,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing :: Markup',
    ),
    packages=('dust',),
)
