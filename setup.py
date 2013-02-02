# -*- coding: utf-8 -*-
"""
Ashes provides a Python implementation of the dust_ templating
language.

.. _dust: http://akdubya.github.com/dustjs/

"""
from setuptools import setup


setup(
    name='ashes',
    version='0.4.0',
    license='BSD',
    author='Mahmoud Hashemi',
    author_email='mahmoudrhashemi@gmail.com',
    url='https://github.com/mahmoud/ashes',
    description='Dust templating for Python',
    long_description=__doc__,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Text Processing :: Markup',
    ),
    py_modules=('ashes',),
    scripts=('ashes.py',),
    platforms='any'
)
