#!/usr/bin/env python

from __future__ import unicode_literals

from binascii import a2b_hex

# Allow direct execution

import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from youtube_dl.blowfish import Blowfish, blowfish_cbc_decrypt

# ECB Test vector data from http://www.mirrors.wiretapped.net/security/cryptography/algorithms/blowfish/blowfish-TESTVECTORS.txt
testvectors = [
    [[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], (0x00000000, 0x00000000), (0x4ef99745, 0x6198dd78)],
    [[0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff], (0xffffffff, 0xffffffff), (0x51866fd5, 0xb85ecb8a)],
    [[0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff], (0x00000000, 0x00000000), (0xf21e9a77, 0xb71c49bc)],
    [[0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11], (0x01234567, 0x89abcdef), (0x7d0cc630, 0xafda1ec7)],
    [[0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x11], (0x11111111, 0x11111111), (0x2466dd87, 0x8b963c9d)],
    [[0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], (0xffffffff, 0xffffffff), (0x014933e0, 0xcdaff6e4)],
    [[0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01], (0x01234567, 0x89abcdef), (0xfa34ec48, 0x47b268b2)],
    [[0x1f, 0x1f, 0x1f, 0x1f, 0x0e, 0x0e, 0x0e, 0x0e], (0x01234567, 0x89abcdef), (0xa7907951, 0x08ea3cae)],
    [[0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], (0x10000000, 0x00000001), (0x7d856f9a, 0x613063f2)],
    [[0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef], (0x11111111, 0x11111111), (0x61f9c380, 0x2281b096)],
    [[0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10], (0x01234567, 0x89abcdef), (0x0aceab0f, 0xc6a0a28d)],
    [[0x7c, 0xa1, 0x10, 0x45, 0x4a, 0x1a, 0x6e, 0x57], (0x01a1d6d0, 0x39776742), (0x59c68245, 0xeb05282b)],
    [[0x01, 0x31, 0xd9, 0x61, 0x9d, 0xc1, 0x37, 0x6e], (0x5cd54ca8, 0x3def57da), (0xb1b8cc0b, 0x250f09a0)],
    [[0x07, 0xa1, 0x13, 0x3e, 0x4a, 0x0b, 0x26, 0x86], (0x0248d438, 0x06f67172), (0x1730e577, 0x8bea1da4)],
    [[0x38, 0x49, 0x67, 0x4c, 0x26, 0x02, 0x31, 0x9e], (0x51454b58, 0x2ddf440a), (0xa25e7856, 0xcf2651eb)],
    [[0x04, 0xb9, 0x15, 0xba, 0x43, 0xfe, 0xb5, 0xb6], (0x42fd4430, 0x59577fa2), (0x353882b1, 0x09ce8f1a)],
    [[0x01, 0x13, 0xb9, 0x70, 0xfd, 0x34, 0xf2, 0xce], (0x059b5e08, 0x51cf143a), (0x48f4d088, 0x4c379918)],
    [[0x01, 0x70, 0xf1, 0x75, 0x46, 0x8f, 0xb5, 0xe6], (0x0756d8e0, 0x774761d2), (0x432193b7, 0x8951fc98)],
    [[0x43, 0x29, 0x7f, 0xad, 0x38, 0xe3, 0x73, 0xfe], (0x762514b8, 0x29bf486a), (0x13f04154, 0xd69d1ae5)],
    [[0x07, 0xa7, 0x13, 0x70, 0x45, 0xda, 0x2a, 0x16], (0x3bdd1190, 0x49372802), (0x2eedda93, 0xffd39c79)],
    [[0x04, 0x68, 0x91, 0x04, 0xc2, 0xfd, 0x3b, 0x2f], (0x26955f68, 0x35af609a), (0xd887e039, 0x3c2da6e3)],
    [[0x37, 0xd0, 0x6b, 0xb5, 0x16, 0xcb, 0x75, 0x46], (0x164d5e40, 0x4f275232), (0x5f99d04f, 0x5b163969)],
    [[0x1f, 0x08, 0x26, 0x0d, 0x1a, 0xc2, 0x46, 0x5e], (0x6b056e18, 0x759f5cca), (0x4a057a3b, 0x24d3977b)],
    [[0x58, 0x40, 0x23, 0x64, 0x1a, 0xba, 0x61, 0x76], (0x004bd6ef, 0x09176062), (0x452031c1, 0xe4fada8e)],
    [[0x02, 0x58, 0x16, 0x16, 0x46, 0x29, 0xb0, 0x07], (0x480d3900, 0x6ee762f2), (0x7555ae39, 0xf59b87bd)],
    [[0x49, 0x79, 0x3e, 0xbc, 0x79, 0xb3, 0x25, 0x8f], (0x437540c8, 0x698f3cfa), (0x53c55f9c, 0xb49fc019)],
    [[0x4f, 0xb0, 0x5e, 0x15, 0x15, 0xab, 0x73, 0xa7], (0x072d43a0, 0x77075292), (0x7a8e7bfa, 0x937e89a3)],
    [[0x49, 0xe9, 0x5d, 0x6d, 0x4c, 0xa2, 0x29, 0xbf], (0x02fe5577, 0x8117f12a), (0xcf9c5d7a, 0x4986adb5)],
    [[0x01, 0x83, 0x10, 0xdc, 0x40, 0x9b, 0x26, 0xd6], (0x1d9d5c50, 0x18f728c2), (0xd1abb290, 0x658bc778)],
    [[0x1c, 0x58, 0x7f, 0x1c, 0x13, 0x92, 0x4f, 0xef], (0x30553228, 0x6d6f295a), (0x55cb3774, 0xd13ef201)],
    [[0xe0, 0xfe, 0xe0, 0xfe, 0xf1, 0xfe, 0xf1, 0xfe], (0x01234567, 0x89abcdef), (0xc39e072d, 0x9fac631d)],
    [[0x01, 0x23, 0x45, 0x67, 0x89, 0xab, 0xcd, 0xef], (0x00000000, 0x00000000), (0x24594688, 0x5754369a)],
    [[0xfe, 0xdc, 0xba, 0x98, 0x76, 0x54, 0x32, 0x10], (0xffffffff, 0xffffffff), (0x6b5c5a9c, 0x5d9e0a5a)]
]


class TestBlowfish(unittest.TestCase):
    def test_koch(self):
        # test vector from Paul Koch's blowfish implementation
        bf = Blowfish(b"TESTKEY")
        l, r = 1, 2

        l, r = bf.encipher(l, r)
        self.assertEqual((l, r), (0xDF333FD2, 0x30A71BB4))
        l, r = bf.decipher(l, r)

        self.assertEqual((l, r), (1, 2))

    def test_vectors(self):
        for key, indata, outdata in testvectors:
            bf = Blowfish(key)
            l, r = bf.encipher(*indata)
            self.assertEqual((l, r), outdata)

    def test_cbc1(self):
        key = a2b_hex(b"0123456789abcdeff0e1d2c3b4a59687")
        iv = a2b_hex(b"fedcba9876543210")
        indata = a2b_hex(b"6b77b4d63006dee605b156e27403979358deb9e7154616d9")
        check = a2b_hex(b"37363534333231204e6f77206973207468652074696d6520")

        outdata = blowfish_cbc_decrypt(indata, key, iv)
        self.assertEqual(outdata, check)


if __name__ == '__main__':
    unittest.main()
