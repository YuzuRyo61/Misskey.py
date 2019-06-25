#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import configparser
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.abspath(__file__ + "/../")))
from Misskey import Misskey, MisskeyUtil, MisskeyInitException, MisskeyAiException, MisskeyAPIException, MisskeyFileException, MisskeyAPITokenException

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
        
        print("\t\t=> Invalid APIToken(i) [MisskeyAPITokenException]")
        self.assertRaises(MisskeyAPITokenException, lambda: Misskey(config['instance']['address'], i="invalid"))
        
        print("\t\t=> No APIToken(i) [MisskeyAiException]")
        self.assertRaises(MisskeyAiException, lambda: self.unit.i())
        
        print("\t\t=> API Error [MisskeyAPIException]")
        self.assertRaises(MisskeyAPIException, lambda: self.unitI.notes_create())

        print("\t\t=> Specified file is not found [MisskeyFileException]")
        self.assertRaises(MisskeyFileException, lambda: self.unitI.drive_files_create("hoge"))
        
        print("DONE\t=> [EXCEPTIONS]\n")

    def test_Util(self):
        print("UNIT\t=> [UTILITY]")
        
        print("\t\t=> hash_apitoken")
        hashed = MisskeyUtil.hash_apitoken(config['key']['accesstoken'], config['key']['appsecret'])
        self.assertEqual(config['key']['i_app_access'], hashed)
        
        print("\t\t=> hash_apitoken => Should usable")
        mk = Misskey(config['instance']['address'], i=hashed)
        mkI = mk.i()
        self.assertEqual(type(mkI), dict)
        
        print("\t\t=> username_available")
        self.assertEqual(type(MisskeyUtil.username_available(config['instance']['address'], "hoge")), dict)

        print("DONE\t=> [UTILITY]\n")

    def test_other(self):
        print("UNIT\t=> [OTHER]")
        
        print("\t\t=> delete apiToken")
        uniti_other = Misskey(config['instance']['address'], i=config['key']['i'])
        del uniti_other.apiToken
        self.assertEqual(uniti_other.apiToken, None)

        print("\t\t=> read address")
        self.assertEqual(uniti_other.address, config['instance']['address'])

        print("DONE\t=> [OTHER]")


    def test_meta(self):
        print("UNIT\t=> meta")
        res = self.unit.meta()
        self.assertEqual(type(res), dict)
        print("DONE\t=> meta\n")

    def test_stats(self):
        print("UNIT\t=> stats")
        res = self.unit.stats()
        self.assertEqual(type(res), dict)
        print("DONE\t=> stats\n")

    def test_i(self):
        print("UNIT\t=> i")

        print("\t\t=> i")
        self.assertEqual(type(self.unitI.i()), dict)

        print("\t\t=> i_favorites")
        self.assertEqual(type(self.unitI.i_favorites()), list)

        print("\t\t=> i_notifications")
        self.assertEqual(type(self.unitI.i_notifications()), list)

        print("\t\t=> i_readAllMessagingMessages")
        self.assertTrue(self.unitI.i_readAllMessagingMessages())

        print("\t\t=> i_readAllUnreadNotes")
        self.assertTrue(self.unitI.i_readAllUnreadNotes())

        print("\t\t=> notifications_markAllAsRead")
        self.assertTrue(self.unitI.notifications_markAllAsRead())

        print("\t\t=> i_update")
        self.assertEqual(type(self.unitI.i_update()), dict)

        print("DONE\t=> i\n")

    def test_notes(self):
        print("UNIT\t=> notes")
        
        print("\t\t=> notes_create")
        res_ncv = self.unitI.notes_create("Misskey.py notes testing...")
        res_vote = self.unitI.notes_create("Misskey.py vote notes testing...", poll=['choice1', 'choice2'])
        self.assertEqual(type(res_ncv), dict)
        
        print("\t\t=> notes_show")
        self.assertEqual(type(self.unitI.notes_show(res_ncv['createdNote']['id'])), dict)

        print("\t\t=> notes_renotes")
        self.assertEqual(type(self.unitI.notes_renotes(res_ncv['createdNote']['id'])), list)

        print("\t\t=> notes_polls_vote")
        self.assertTrue(self.unitI.notes_polls_vote(res_vote['createdNote']['id'], 0))

        print("\t\t=> i_pin")
        self.assertEqual(type(self.unitI.i_pin(res_ncv['createdNote']['id'])), dict)

        print("\t\t=> i_unpin")
        self.assertEqual(type(self.unitI.i_unpin(res_ncv['createdNote']['id'])), dict)

        print("\t\t=> notes_delete")
        self.assertTrue(self.unitI.notes_delete(res_ncv['createdNote']['id']))
        self.assertTrue(self.unitI.notes_delete(res_vote['createdNote']['id']))
        
        print("\t\t=> notes_reactions_create")
        self.assertTrue(self.unitI.notes_reactions_create(config['note']['targetReaction'], 0))

        print("\t\t=> notes_reactions")
        self.assertEqual(type(self.unitI.notes_reactions(config['note']['targetReaction'])), list)

        print("\t\t=> notes_reactions_delete")
        self.assertTrue(self.unitI.notes_reactions_delete(config['note']['targetReaction']))

        print("\t\t=> notes_favorites_create")
        self.assertTrue(self.unitI.notes_favorites_create(config['note']['targetReaction']))

        print("\t\t=> notes_favorites_delete")
        self.assertTrue(self.unitI.notes_favorites_delete(config['note']['targetReaction']))

        print("\t\t=> notes")
        self.assertEqual(type(self.unitI.notes()), list)

        print("\t\t=> notes_globalTimeline")
        self.assertEqual(type(self.unitI.notes_globalTimeline()), list)

        print("\t\t=> notes_hybridTimeline")
        self.assertEqual(type(self.unitI.notes_hybridTimeline()), list)

        print("\t\t=> notes_localTimeline")
        self.assertEqual(type(self.unitI.notes_localTimeline()), list)

        print("\t\t=> notes_userListTimeline")
        self.assertEqual(type(self.unitI.notes_userListTimeline(config['lists']['target'])), list)

        print("DONE\t=> notes\n")
    
    def test_users(self):
        print("UNIT\t=> users")

        print("\t\t=> users")
        self.assertEqual(type(self.unit.users()), list)

        print("\t\t=> users_show")
        self.assertEqual(type(self.unit.users_show(userId=config['user']['target'])), dict)

        print("\t\t=> users_show (many)")
        self.assertEqual(type(self.unit.users_show(userIds=[config['user']['target']])), list)

        print("\t\t=> users_notes")
        self.assertEqual(type(self.unitI.users_notes(config['user']['target'])), list)

        print("\t\t=> users_lists_create")
        ulc = self.unitI.users_lists_create("test")
        self.assertEqual(type(ulc), dict)

        print("\t\t=> users_lists_push")
        self.assertTrue(self.unitI.users_lists_push(ulc['id'], config['user']['target']))

        print("\t\t=> users_lists_show")
        self.assertEqual(type(self.unitI.users_lists_show(ulc['id'])), dict)

        print("\t\t=> users_lists_pull")
        self.assertTrue(self.unitI.users_lists_pull(ulc['id'], config['user']['target']))

        print("\t\t=> users_lists_update")
        self.assertEqual(type(self.unitI.users_lists_update(ulc['id'], "test_rename")), dict)

        print("\t\t=> users_lists_delete")
        self.assertTrue(self.unitI.users_lists_delete(ulc['id']))

        print("\t\t=> users_lists_list")
        self.assertEqual(type(self.unitI.users_lists_list()), list)

        print("\t\t=> users_followers")
        self.assertEqual(type(self.unit.users_followers(userId=config['user']['target'])), list)

        print("\t\t=> users_following")
        self.assertEqual(type(self.unit.users_following(userId=config['user']['target'])), list)

        print("\t\t=> following_create")
        self.assertEqual(type(self.unitI.following_create(config['user']['target'])), dict)

        print("\t\t=> following_delete")
        self.assertEqual(type(self.unitI.following_delete(config['user']['target'])), dict)

        print("\t\t=> mute_create")
        self.assertTrue(self.unitI.mute_create(config['user']['target']))

        print("\t\t=> mute_list")
        self.assertEqual(type(self.unitI.mute_list()), list)

        print("\t\t=> mute_delete")
        self.assertTrue(self.unitI.mute_delete(config['user']['target']))

        print("\t\t=> blocking_create")
        self.assertEqual(type(self.unitI.blocking_create(config['user']['target'])), dict)

        print("\t\t=> blocking_list")
        self.assertEqual(type(self.unitI.blocking_list()), list)

        print("\t\t=> blocking_delete")
        self.assertEqual(type(self.unitI.blocking_delete(config['user']['target'])), dict)

        print("DONE\t=> users\n")

    def test_drive(self):
        print("UNIT\t=> drive")
        
        print("\t\t=> drive")
        self.assertEqual(type(self.unitI.drive()), dict)
        
        print("\t\t=> drive_files")
        self.assertEqual(type(self.unitI.drive_files()), list)
        
        print("\t\t=> drive_files_create")
        uploadRes = self.unitI.drive_files_create(os.path.dirname(os.path.abspath(__file__)) + "/uploadTarget.png")
        self.assertEqual(type(uploadRes), dict)

        print("\t\t=> drive_files_uploadFromUrl")
        uploadRes_url = self.unitI.drive_files_uploadFromUrl(config['drive']['targetUrl'])
        self.assertEqual(type(uploadRes_url), dict)

        print("\t\t=> drive_files_attachedNotes")
        self.assertEqual(type(self.unitI.drive_files_attachedNotes(uploadRes['id'])), list)

        print("\t\t=> drive_files_checkExistence")
        self.assertTrue(self.unitI.drive_files_checkExistence(uploadRes['md5']))
        self.assertFalse(self.unitI.drive_files_checkExistence("hoge"))

        print("\t\t=> drive_files_find")
        self.assertEqual(type(self.unitI.drive_files_find("uploadTarget.png")), list)

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
        
        print("\t\t=> drive_folders_find")
        self.assertEqual(type(self.unitI.drive_folders_find("testFolder")), list)

        print("\t\t=> drive_folders_show")
        self.assertEqual(type(self.unitI.drive_folders_show(createFolder['id'])), dict)

        print("\t\t=> drive_folders_update")
        self.assertEqual(type(self.unitI.drive_folders_update(createFolder['id'], name="updatedTestFolder")), dict)

        print("\t\t=> drive_folders_delete")
        self.assertTrue(type(self.unitI.drive_folders_delete(createFolder['id'])))

        print("\t\t=> drive_stream")
        self.assertEqual(type(self.unitI.drive_stream()), list)

        print("DONE\t=> drive\n")

    def test_messaging(self):
        print("UNIT\t=> messaging")
        
        print("\t\t=> messaging_history")
        self.assertEqual(type(self.unitI.messaging_history()), list)

        print("\t\t=> messaging_messages")
        self.assertEqual(type(self.unitI.messaging_messages(config['user']['target'])), list)

        print("\t\t=> messaging_messages_create")
        mmc = self.unitI.messaging_messages_create(config['user']['target'], text="It works!")
        self.assertEqual(type(mmc), dict)

        print("\t\t=> messaging_messages_read")
        self.assertTrue(self.unitI.messaging_messages_read(config['messages']['target']))

        print("\t\t=> messaging_messages_delete")
        self.assertTrue(self.unitI.messaging_messages_delete(mmc['id']))

def TESTSUITE():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(MisskeyPyUnitTest))
    return suite

if __name__ == "__main__":
    unittest.main()
