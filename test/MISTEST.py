#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
from Misskey import Misskey

class MISSKEY_UNITTEST(unittest.TestCase):
    def init_test(self):
        misskey_xyz = Misskey()
        misskey_xyz.meta()

        yuzulia_xyz = Misskey("yuzulia.xyz")
        yuzulia_xyz.meta()

def UNITTEST_FUNCTION():
    __UNITTEST = unittest.TestSuite()
    __UNITTEST.addTests(unittest.makeSuite(MISSKEY_UNITTEST))
    return __UNITTEST