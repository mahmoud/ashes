# -*- coding: utf-8 -*-
"""
Ashes provides a Python implementation of dust_, a lightweight
templating language that makes it easy to create purely data-driven
templates that work equally well on servers and clients.

Ashes is pure Python and is tested on Python 2.7, 3.2, and PyPy.

.. _dust: http://akdubya.github.com/dustjs/

"""
from setuptools import setup


setup(
    name='ashes',
    version='0.5.2dev',
    license='BSD',
    author='Mahmoud Hashemi',
    author_email='mahmoudrhashemi@gmail.com',
    url='https://github.com/mahmoud/ashes',
    description='Lightweight templating for Python (a la dust)',
    long_description=__doc__,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup',
    ),
    py_modules=('ashes',),
    scripts=('ashes.py',),
    platforms='any'
)
