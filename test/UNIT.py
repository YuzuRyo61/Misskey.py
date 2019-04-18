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
        res_ncv = self.unitI.notes_create("Misskey.py notes testing...")
        self.assertEqual(type(res_ncv), dict)
        
        print("\t\t=> notes_show")
        self.assertEqual(type(self.unitI.notes_show(res_ncv['createdNote']['id'])), dict)

        print("\t\t=> notes_renotes")
        self.assertEqual(type(self.unitI.notes_renotes(res_ncv['createdNote']['id'])), list)

        print("\t\t=> notes_delete")
        self.assertTrue(self.unitI.notes_delete(res_ncv['createdNote']['id']))
        
        print("\t\t=> notes_reactions_create")
        self.assertTrue(self.unitI.notes_reactions_create(config['note']['targetReaction'], 0))

        print("\t\t=> notes_reactions_delete")
        self.assertTrue(self.unitI.notes_reactions_delete(config['note']['targetReaction']))

        print("SUCCESS\t=> notes\n")
    
    def test_users(self):
        print("UNIT\t=> users")

        print("\t\t=> users_show")
        self.assertEqual(type(self.unit.users_show(userId=config['user']['target'])), dict)

        print("\t\t=> users_show (many)")
        self.assertEqual(type(self.unit.users_show(userIds=[config['user']['target']])), list)

        print("\t\t=> users_followers")
        self.assertEqual(type(self.unit.users_followers(userId=config['user']['target'])), list)

        print("\t\t=> users_following")
        self.assertEqual(type(self.unit.users_following(userId=config['user']['target'])), list)

        print("\t\t=> following_create")
        self.assertEqual(type(self.unitI.following_create(config['user']['target'])), dict)

        print("\t\t=> following_delete")
        self.assertEqual(type(self.unitI.following_delete(config['user']['target'])), dict)

        print("SUCCESS\t=> users\n")

    def test_drive(self):
        print("UNIT\t=> drive")
        
        print("\t\t=> drive")
        self.assertEqual(type(self.unitI.drive()), dict)
        
        print("\t\t=> drive_files")
        self.assertEqual(type(self.unitI.drive_files()), list)
        
        print("\t\t=> drive_files_create")
        uploadRes = self.unitI.drive_files_create(os.path.dirname(os.path.abspath(__file__)) + "/uploadTarget.png")
        self.assertEqual(type(uploadRes), dict)

        print("\t\t=> drive_uploadFromUrl")
        uploadRes_url = self.unitI.drive_files_uploadFromUrl(config['drive']['targetUrl'])
        self.assertEqual(type(uploadRes_url), dict)

        print("\t\t=> drive_files_show")
        self.assertEqual(type(self.unitI.drive_files_show(fileId=uploadRes['id'])), dict)

        print("\t\t=> drive_files_update")
        self.assertEqual(type(self.unitI.drive_files_update(uploadRes['id'], name="updatedTarget.png")), dict)

        print("\t\t=> drive_files_delete")
        self.assertTrue(self.unitI.drive_files_delete(uploadRes['id']))
        self.assertTrue(self.unitI.drive_files_delete(uploadRes_url['id']))
        
        print("\t\t=> drive_folders")
        self.assertEqual(type(self.unitI.drive_folders()), list)

        print("\t\t=> drive_folders_create")
        createFolder = self.unitI.drive_folders_create("testFolder")
        self.assertEqual(type(createFolder), dict)
        
        print("\t\t=> drive_folders_show")
        self.assertEqual(type(self.unitI.drive_folders_show(createFolder['id'])), dict)

        print("\t\t=> drive_folders_update")
        self.assertEqual(type(self.unitI.drive_folders_update(createFolder['id'], name="updatedTestFolder")), dict)

        print("\t\t=> drive_folders_delete")
        self.assertTrue(type(self.unitI.drive_folders_delete(createFolder['id'])))

        print("SUCCESS\t=> drive\n")

def TESTSUITE():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(MisskeyPyUnitTest))
    return suite

if __name__ == "__main__":
    unittest.main()
