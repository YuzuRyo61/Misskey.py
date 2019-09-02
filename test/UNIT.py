#!/usr/bin/env python3
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

    def test_exception_init(self):
        self.assertRaises(MisskeyInitException, lambda: Misskey('yuzulia.com'))
        
    def test_exception_apitoken(self):
        self.assertRaises(MisskeyAPITokenException, lambda: Misskey(config['instance']['address'], i="invalid"))
    
    def test_exception_ai(self):
        self.assertRaises(MisskeyAiException, lambda: self.unit.i())
        
    def test_exception_api(self):
        self.assertRaises(MisskeyAPIException, lambda: self.unitI.notes_create())

    def test_exception_file(self):
        self.assertRaises(MisskeyFileException, lambda: self.unitI.drive_files_create("hoge"))
        
    def test_Util_hashapitoken(self):
        hashed = MisskeyUtil.hash_apitoken(config['key']['accesstoken'], config['key']['appsecret'])
        self.assertEqual(config['key']['i_app_access'], hashed)
        
        mk = Misskey(config['instance']['address'], i=hashed)
        mkI = mk.i()
        self.assertEqual(type(mkI), dict)
        
    def test_Util_usernameavaliable(self):
        self.assertEqual(type(MisskeyUtil.username_available(config['instance']['address'], "hoge")), dict)

    def test_deletable_apiToken(self):
        uniti_other = Misskey(config['instance']['address'], i=config['key']['i'])
        del uniti_other.apiToken
        self.assertEqual(uniti_other.apiToken, None)

    def test_read_address(self):
        self.assertEqual(self.unit.address, config['instance']['address'])

    def test_meta(self):
        res = self.unit.meta()
        self.assertEqual(type(res), dict)

    def test_stats(self):
        res = self.unit.stats()
        self.assertEqual(type(res), dict)

    def test_i(self):
        self.assertEqual(type(self.unitI.i()), dict)

    def test_i_favorites(self):
        self.assertEqual(type(self.unitI.i_favorites()), list)

    def test_i_notifications(self):
        self.assertEqual(type(self.unitI.i_notifications()), list)

    def test_i_readAllMessagingMessages(self):
        self.assertTrue(self.unitI.i_readAllMessagingMessages())

    def test_i_readAllUnreadNotes(self):
        self.assertTrue(self.unitI.i_readAllUnreadNotes())

    def test_notifications_markAllAsRead(self):
        self.assertTrue(self.unitI.notifications_markAllAsRead())

    def test_i_update(self):
        self.assertEqual(type(self.unitI.i_update()), dict)

    def test_0_notes_create(self):
        res_ncv = self.unitI.notes_create("Misskey.py notes testing...")
        res_vote = self.unitI.notes_create("Misskey.py vote notes testing...", poll=['choice1', 'choice2'])
        self.assertEqual(type(res_ncv), dict)
        self.__class__.noteId = res_ncv['createdNote']['id']
        self.__class__.noteId_vote = res_vote['createdNote']['id']
    
    def test_1_notes_show(self):
        self.assertEqual(type(self.unitI.notes_show(self.__class__.noteId)), dict)

    def test_1_notes_renotes(self):
        self.assertEqual(type(self.unitI.notes_renotes(self.__class__.noteId)), list)

    def test_1_notes_polls_vote(self):
        self.assertTrue(self.unitI.notes_polls_vote(self.__class__.noteId_vote, 0))

    def test_1_i_pin(self):
        self.assertEqual(type(self.unitI.i_pin(self.__class__.noteId_vote)), dict)

    def test_8_i_unpin(self):
        self.assertEqual(type(self.unitI.i_unpin(self.__class__.noteId_vote)), dict)


    def test_9_notes_delete(self):
        self.assertTrue(self.unitI.notes_delete(self.__class__.noteId))
        self.assertTrue(self.unitI.notes_delete(self.__class__.noteId_vote))
        
    def test_0_notes_reactions_create(self):
        self.assertTrue(self.unitI.notes_reactions_create(config['note']['targetReaction'], 0))

    def test_1_notes_reactions(self):
        self.assertEqual(type(self.unitI.notes_reactions(config['note']['targetReaction'])), list)

    def test_9_notes_reactions_delete(self):
        self.assertTrue(self.unitI.notes_reactions_delete(config['note']['targetReaction']))

    def test_0_notes_favorites_create(self):
        self.assertTrue(self.unitI.notes_favorites_create(config['note']['targetReaction']))

    def test_9_notes_favorites_delete(self):
        self.assertTrue(self.unitI.notes_favorites_delete(config['note']['targetReaction']))

    def test_notes(self):
        self.assertEqual(type(self.unitI.notes()), list)

    def test_globalTimeline(self):
        self.assertEqual(type(self.unitI.notes_globalTimeline()), list)

    def test_hybridTimeline(self):
        self.assertEqual(type(self.unitI.notes_hybridTimeline()), list)

    def test_localTimeline(self):
        self.assertEqual(type(self.unitI.notes_localTimeline()), list)

    def test_userListTimeline(self):
        self.assertEqual(type(self.unitI.notes_userListTimeline(config['lists']['target'])), list)
    
    def test_users(self):
        self.assertEqual(type(self.unit.users()), list)

    def test_users_show(self):
        self.assertEqual(type(self.unit.users_show(userId=config['user']['target'])), dict)

    def test_users_showMulti(self):
        self.assertEqual(type(self.unit.users_show(userIds=[config['user']['target']])), list)

    def test_users_notes(self):
        self.assertEqual(type(self.unitI.users_notes(config['user']['target'])), list)

    def test_0_users_lists_create(self):
        ulc = self.unitI.users_lists_create("test")
        self.assertEqual(type(ulc), dict)
        self.__class__.listId = ulc['id']

    def test_1_users_lists_push(self):
        self.assertTrue(self.unitI.users_lists_push(self.__class__.listId, config['user']['target']))

    def test_1_users_lists_show(self):
        self.assertEqual(type(self.unitI.users_lists_show(self.__class__.listId)), dict)

    def test_8_users_lists_pull(self):
        self.assertTrue(self.unitI.users_lists_pull(self.__class__.listId, config['user']['target']))

    def test_8_users_lists_update(self):
        self.assertEqual(type(self.unitI.users_lists_update(self.__class__.listId, "test_rename")), dict)

    def test_9_users_lists_delete(self):
        self.assertTrue(self.unitI.users_lists_delete(self.__class__.listId))

    def test_users_lists_list(self):
        self.assertEqual(type(self.unitI.users_lists_list()), list)

    def test_users_followers(self):
        self.assertEqual(type(self.unit.users_followers(userId=config['user']['target'])), list)

    def test_users_following(self):
        self.assertEqual(type(self.unit.users_following(userId=config['user']['target'])), list)

    def test_0_following_create(self):
        self.assertEqual(type(self.unitI.following_create(config['user']['target'])), dict)

    def test_0_following_delete(self):
        self.assertEqual(type(self.unitI.following_delete(config['user']['target'])), dict)

    def test_0_mute_create(self):
        self.assertTrue(self.unitI.mute_create(config['user']['target']))

    def test_mute_list(self):
        self.assertEqual(type(self.unitI.mute_list()), list)

    def test_9_mute_delete(self):
        self.assertTrue(self.unitI.mute_delete(config['user']['target']))

    def test_0_blocking_create(self):
        self.assertEqual(type(self.unitI.blocking_create(config['user']['target'])), dict)

    def test_0_blocking_list(self):
        self.assertEqual(type(self.unitI.blocking_list()), list)

    def test_0_blocking_delete(self):
        self.assertEqual(type(self.unitI.blocking_delete(config['user']['target'])), dict)

    def test_drive(self):
        self.assertEqual(type(self.unitI.drive()), dict)
        
    def test_drive_files(self):
        self.assertEqual(type(self.unitI.drive_files()), list)
        
    def test_0_drive_files_create(self):
        self.__class__.driveFiles = self.unitI.drive_files_create(os.path.dirname(os.path.abspath(__file__)) + "/uploadTarget.png")
        self.assertEqual(type(self.__class__.driveFiles), dict)
    
    def test_0_drive_files_uploadFromUrl(self):
        self.__class__.driveFilesUrl = self.unitI.drive_files_uploadFromUrl(config['drive']['targetUrl'])
        self.assertEqual(type(self.__class__.driveFilesUrl), dict)

    def test_1_drive_files_attachedNotes(self):
        self.assertEqual(type(self.unitI.drive_files_attachedNotes(self.__class__.driveFiles['id'])), list)

    def test_1_drive_files_checkExistence(self):
        self.assertTrue(self.unitI.drive_files_checkExistence(self.__class__.driveFiles['md5']))
        self.assertTrue(self.unitI.drive_files_checkExistence(self.__class__.driveFilesUrl['md5']))
        self.assertFalse(self.unitI.drive_files_checkExistence("hoge"))

    def test_1_drive_files_find(self):
        self.assertEqual(type(self.unitI.drive_files_find("uploadTarget.png")), list)

    def test_1_drive_files_show(self):
        self.assertEqual(type(self.unitI.drive_files_show(fileId=self.__class__.driveFiles['id'])), dict)

    def test_2_drive_files_update(self):
        self.assertEqual(type(self.unitI.drive_files_update(self.__class__.driveFiles['id'], name="updatedTarget.png")), dict)

    def test_9_drive_files_delete(self):
        self.assertTrue(self.unitI.drive_files_delete(self.__class__.driveFiles['id']))
        self.assertTrue(self.unitI.drive_files_delete(self.__class__.driveFilesUrl['id']))
        
    def test_drive_folders(self):
        self.assertEqual(type(self.unitI.drive_folders()), list)

    def test_0_drive_folders_create(self):
        self.__class__.driveFolders = self.unitI.drive_folders_create("testFolder")
        self.assertEqual(type(self.__class__.driveFolders), dict)
        
    def test_1_drive_folders_find(self):
        self.assertEqual(type(self.unitI.drive_folders_find("testFolder")), list)

    def test_1_drive_folders_show(self):
        self.assertEqual(type(self.unitI.drive_folders_show(self.__class__.driveFolders['id'])), dict)

    def test_2_drive_folders_update(self):
        self.assertEqual(type(self.unitI.drive_folders_update(self.__class__.driveFolders['id'], name="updatedTestFolder")), dict)

    def test_9_drive_folders_delete(self):
            self.assertTrue(type(self.unitI.drive_folders_delete(self.__class__.driveFolders['id'])))

    def test_drive_stream(self):
        self.assertEqual(type(self.unitI.drive_stream()), list)

    def test_messaging_history(self):
        self.assertEqual(type(self.unitI.messaging_history()), list)

    def test_messaging_messages(self):
        self.assertEqual(type(self.unitI.messaging_messages(config['user']['target'])), list)

    def test_0_messaging_messages_create(self):
        mmc = self.unitI.messaging_messages_create(config['user']['target'], text="It works!")
        self.assertEqual(type(mmc), dict)
        self.__class__.messagingId = mmc['id']

    def test_messaging_messages_read(self):
        self.assertTrue(self.unitI.messaging_messages_read(config['messages']['target']))

    def test_9_messaging_messages_delete(self):
        self.assertTrue(self.unitI.messaging_messages_delete(self.__class__.messagingId))

def TESTSUITE():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(MisskeyPyUnitTest))
    return suite

if __name__ == "__main__":
    unittest.main()
