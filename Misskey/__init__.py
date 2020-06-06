# -*- coding: utf-8 -*-
"""
Misskey.py

:copyright: (C) 2019 YuzuRyo61.
:license: MIT License, see LICENSE for more details.
"""

from Misskey.Misskey import Misskey
from Misskey.Exceptions import *

__all__ = [
    'Misskey',
    'MisskeyAiException',
    'MisskeyInitException',
    'MisskeyAPIException',
    'MisskeyFileException',
    'MisskeyAPITokenException',
    'MisskeyNotImplementedVersionException',
    'MisskeyMiAuthCheckException'
]

__version__ = "3.0.0"
