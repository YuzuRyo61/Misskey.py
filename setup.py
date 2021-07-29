#!/usr/bin/env python3

from setuptools import setup

try:
    # noinspection PyUnresolvedReferences
    from m2r import parse_from_file
except ImportError:
    ld = ':code:`Could not load m2r module.`'
else:
    ld = parse_from_file('README.md')

from misskey import __version__ as mkp_version

setup(
    name='Misskey.py',
    version=mkp_version,
    description='The misskey library for Python. misskey is made by syuilo.',
    long_description=ld,
    keywords="misskey API syuilo",
    author='YuzuRyo61',
    url='https://github.com/YuzuRyo61/Misskey.py',
    license='MIT',
    install_requires=[
        'requests'
    ],
    packages=['misskey'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Japanese',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Development Status :: 5 - Production/Stable',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet'
    ]
)
