#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import configparser
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../")))
from Misskey import Misskey, MisskeyUtil, MisskeyInitException, MisskeyAiException, MisskeyAPIException, MisskeyFileException

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

        print("\t\t=> Specified file is not found [MisskeyFileException]")
        self.assertRaises(MisskeyFileException, lambda: self.unitI.drive_files_create("hoge"))
        
        print("SUCCESS\t=> [EXCEPTIONS]\n")

    def test_Util(self):
        print("UNIT\t=> [UTILITIY]")
        
        print("\t\t=> hash_apitoken")
        hashed = MisskeyUtil.hash_apitoken(config['key']['accesstoken'], config['key']['appsecret'])
        self.assertEqual(config['key']['i_app_access'], hashed)
        
        print("\t\t=> hash_apitoken => Should usable")
        mk = Misskey(config['instance']['address'], i=hashed)
        mkI = mk.i()
        self.assertEqual(type(mkI), dict)
        
        print("SUCCESS\t=> [UTILITY]\n")

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
        
        print("\t\t=> notes_create => Valid (Normal)")
        res_ncv = self.unitI.notes_create("Misskey.py notes_create testing...")
        self.assertEqual(type(res_ncv), dict)
        time.sleep(1)
        
        print("\t\t=> notes_delete => Valid")
        self.assertTrue(self.unitI.notes_delete(res_ncv['createdNote']['id']))
                
        print("SUCCESS\t=> notes\n")
    
    def test_drive(self):
        print("UNIT\t=> drive")
        
        print("\t\t=> drive")
        self.assertEqual(type(self.unitI.drive()), dict)
        
        print("\t\t=> drive_files")
        self.assertEqual(type(self.unitI.drive_files()), list)
        
        print("\t\t=> drive_files_upload")
        uploadRes = self.unitI.drive_files_create(os.path.dirname(os.path.abspath(__file__)) + "/uploadTarget.png")
        self.assertEqual(type(uploadRes), dict)
        
        print("\t\t=> drive_files_delete")
        self.assertTrue(self.unitI.drive_files_delete(uploadRes['id']))
        
        print("\t\t=> drive_uploadFromUrl")
        uploadRes = self.unitI.drive_files_uploadFromUrl(config['drive']['targetUrl'])
        self.assertEqual(type(uploadRes), dict)
        time.sleep(1)
        self.assertTrue(self.unitI.drive_files_delete(uploadRes['id']))
        
        print("SUCCESS\t=> drive\n")

if __name__ == "__main__":
    unittest.main()
