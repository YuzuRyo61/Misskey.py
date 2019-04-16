#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import configparser
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../")))
from Misskey import Misskey, MisskeyUtil, MisskeyInitException, MisskeyAiException, MisskeyAPIException

config = configparser.ConfigParser()
config.read(os.path.dirname(os.path.abspath(__file__)) + "/env.ini")

class MisskeyPyUnitTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.unit = Misskey(config['instance']['address'])
        cls.unitI = Misskey(config['instance']['address'], i=config['key']['i'])

    def test_exceptions(self):
        print("UNIT\t=> [EXCEPTIONS]")
        print("\t\t=> Invalid Address [MisskeyInitException]")
        self.assertRaises(MisskeyInitException, lambda: Misskey('yuzulia.com'))
        print("\t\t=> Invalid APIToken(i) [MisskeyInitException]")
        self.assertRaises(MisskeyInitException, lambda: Misskey(config['instance']['address'], i="invalid"))
        print("\t\t=> No APIToken(i) [MisskeyAiException]")
        self.assertRaises(MisskeyAiException, lambda: self.unit.i())
        print("\t\t=> API Error [MisskeyAPIException]")
        self.assertRaises(MisskeyAPIException, lambda: self.unitI.notes_create())
        print("SUCCESS\t=> [EXCEPTIONS]\n")

    def test_meta(self):
        print("UNIT\t=> meta")
        res = self.unit.meta()
        self.assertEqual(type(res), dict)
        print("SUCCESS\t=> meta\n")

    def test_stats(self):
        print("UNIT\t=> stats")
        res = self.unit.stats()
        self.assertEqual(type(res), dict)
        print("SUCCESS\t=> status\n")

    def test_i(self):
        print("UNIT\t=> i")
        res = self.unitI.i()
        self.assertEqual(type(res), dict)
        print("SUCCESS\t=> i\n")

    def test_notes(self):
        print("UNIT\t=> notes")
        print("\t\t=> notes_create")
        print("\t\t=> notes_create => Valid")
        res_ncv = self.unitI.notes_create("Misskey.py notes_create testing...")
        self.assertEqual(type(res_ncv), dict)
        time.sleep(1)
        print("\t\t=> notes_delete => Valid")
        self.assertTrue(self.unitI.notes_delete(res_ncv['createdNote']['id']))
        print("SUCCESS\t=> notes")

if __name__ == "__main__":
    unittest.main()