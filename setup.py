#!/usr/bin/env python3
from setuptools import setup, find_packages
setup(
    name='Misskey.py',
    version='0.0.1',
    description='The Misskey library for Python. Misskey is made by syuilo.',
    author='YuzuRyo61',
    author_mail='yuzuryo61@yuzulia.com',
    url='https://github.com/YuzuRyo61/Misskey.py',
    license='MIT',
    install_requires=[
        'requests'
    ],
    packages=find_packages(exclude=('sample', 'docs', 'tests'))
)