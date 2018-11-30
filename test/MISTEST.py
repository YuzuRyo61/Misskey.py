#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

# MISSKEY LIBRARY
from Misskey import Misskey

class MISSKEY_UNITTEST(unittest.TestCase):
	def init_test(self):
		misskey_xyz = Misskey()
		misskey_xyz_meta = misskey_xyz.meta()

		yuzulia_xyz = Misskey("yuzulia.xyz")
		yuzulia_xyz_meta = yuzulia_xyz.meta()
		
		self.assertEqual(misskey_xyz_meta['name'], "Misskey")
		self.assertEqual(misskey_xyz_meta['maintainer']['name'], "syuilo")
		self.assertEqual(misskey_xyz_meta['recaptchaSiteKey'], "6Ldd8foSAAAAAPzLf76PvjZmho4F60THwnlpPPA0")
		self.assertEqual(misskey_xyz_meta['swPublickey'], "BAdGx9Kav70kMX2zNZAjqxVPlRIY3bKLlxTDeW6Epm_JV4Dy3EJpQHRJUwhDFDXEcqCf4-b7WWVw6fb9bHT3SZg")
		
		self.assertEqual(yuzulia_xyz_meta['name'], "Yuzulia-MisSocial")
		self.assertEqual(yuzulia_xyz_meta['maintainer']['name'], "YuzuRyo61")
		self.assertEqual(yuzulia_xyz_meta['recaptchaSiteKey'], "6LdXAV4UAAAAAOG79G1LjLuWrKWEAMG4igg4DVBb")
		self.assertEqual(yuzulia_xyz_meta['swPublickey'], "BI-glY6AQIEaVoGoOfhdiN__Ne82G_Lu_8vaqEKU5jS9z55UT8O4MaMGwyKRDAMGgDFgsXP6DxbzaxLgY7dfP9w")

def UNITTEST_FUNCTION():
	__UNITTEST = unittest.TestSuite()
	__UNITTEST.addTests(unittest.makeSuite(MISSKEY_UNITTEST))
	return __UNITTEST