# -*- coding: utf-8 -*-
import calendar

import unittest

__author__ = 'Alexander Pikovsky'



class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(Test)