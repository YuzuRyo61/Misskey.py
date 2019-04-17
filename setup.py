#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from m2r import parse_from_file
import sys

sys.path.append('./test')

ld = parse_from_file('README.md')

setup(
    name='Misskey.py',
    version='1.0.0',
    description='The Misskey library for Python. Misskey is made by syuilo.',
	long_description=ld,
	test_suite='UNIT.TESTSUITE',
	keywords="Misskey, API, syuilo, Ai",
    author='YuzuRyo61',
    url='https://github.com/YuzuRyo61/Misskey.py',
    license='MIT',
    install_requires=[
        'requests',
        'websocket-client'
    ],
    packages=find_packages(exclude=('sample', 'docs')),
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Natural Language :: Japanese',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Software Development :: Libraries',
		'Development Status :: 4 - Beta',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet'
	]
)
