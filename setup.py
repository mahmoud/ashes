# -*- coding: utf-8 -*-
"""
Ashes provides a Python implementation of dust_, a lightweight
templating language that makes it easy to create purely data-driven
templates that work equally well on servers and clients.

Ashes is pure Python and is tested on Python 2.7, 3.x, and PyPy.

.. _dust: http://akdubya.github.com/dustjs/

"""
from setuptools import setup

from ashes import (__version__,
                   __author__,
                   __contact__,
                   __url__,
                   __license__)

setup(
    name='ashes',
    version=__version__,
    author=__author__,
    author_email=__contact__,
    license=__license__,
    url=__url__,
    description='Lightweight templating for Python (a la dust.js)',
    long_description=__doc__,
    py_modules=('ashes',),
    scripts=('ashes.py',),
    platforms='any',
    entry_points={'console_scripts': ['ashes = ashes:main']},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: JavaScript',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup'],
)
