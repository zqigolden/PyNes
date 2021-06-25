import unittest
from pynes import ppu

class TestDeviceMethods(unittest.TestCase):
    def testSetflag(self):
        A =      0b110011
        B =      0b111000
        mask =   0b001110
        expect = 0b111001
        self.assertEqual(ppu.set_flag(A, B, mask), expect)

if __name__ == '__main__':
    unittest.main()