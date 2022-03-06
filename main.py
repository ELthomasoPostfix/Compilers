import unittest
from testing.test_listener import ListenerTestCase


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ListenerTestCase('test_default_listener_behavior'))
    return suite



if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
