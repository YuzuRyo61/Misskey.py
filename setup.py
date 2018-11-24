#!/usr/bin/env python3
from setuptools import setup, find_packages
import sys

sys.path.append('./test')

setup(
    name='Misskey.py',
    version='0.3.1',
    description='The Misskey library for Python. Misskey is made by syuilo.',
    author='YuzuRyo61',
    url='https://github.com/YuzuRyo61/Misskey.py',
    license='MIT',
    install_requires=[
        'requests',
        'websocket-client'
    ],
    packages=find_packages(exclude=('sample', 'docs', 'tests')),
    test_suite = 'MISTEST.UNITTEST_FUNCTION'
)
