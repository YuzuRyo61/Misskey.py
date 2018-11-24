#!/usr/bin/env python3
from setuptools import setup, find_packages
import sys

sys.path.append('./test')

with open('README.md', encoding="utf-8") as df:
	ld = df.read()

setup(
    name='Misskey.py',
    version='0.3.1',
    description='The Misskey library for Python. Misskey is made by syuilo.',
	long_description=ld,
	keywords="Misskey, API, syuilo",
    author='YuzuRyo61',
    url='https://github.com/YuzuRyo61/Misskey.py',
    license='MIT',
    install_requires=[
        'requests',
        'websocket-client'
    ],
    packages=find_packages(exclude=('sample', 'docs', 'tests')),
    test_suite = 'MISTEST.UNITTEST_FUNCTION',
	classifiers=[
		'License :: OSI Approved :: MIT License',
		'Natural Language :: Japanese',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Software Development :: Libraries',
		'Development Status :: 3 - Alpha',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet'
	]
)
