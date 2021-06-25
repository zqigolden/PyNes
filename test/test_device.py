import unittest
from pynes.device import Device

class TestDeviceMethods(unittest.TestCase):
    def testStr(self):
        device = Device(name='test')
        device2 = Device()
        print(str(device2))
        self.assertEqual(str(device), 'test()')
        self.assertTrue(str(device2).startswith('Device'))

    def testABM(self):
        device = Device()
        with self.assertRaises(NotImplementedError):
            device.read(0x0000)
        with self.assertRaises(NotImplementedError):
            device.write(0x0000, 1)

if __name__ == '__main__':
    unittest.main()