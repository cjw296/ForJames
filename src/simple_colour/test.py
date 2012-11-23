'''
Created on Nov 22, 2012

@author: peterb
'''
import unittest
from simple_colour.control import Control
echo = False

import logging
logging.basicConfig(level=logging.DEBUG)


class Test(unittest.TestCase):


    def setUp(self):
        self.control = Control(echo=echo)
        self.control._accl_key_ = 1


    def tearDown(self):
        self.control._dispose_()


    def testAdd(self):
        self.control.add_colour("red")
        self.control.vote("red")
        self.control.vote("red")
        row = self.control.colours()[0]
        self.assertEquals(row,(1,"red",2))


    def testVote(self):
        self.control.vote("red")
        self.control.vote("red")
        row = self.control.colours()[0]
        self.assertEquals(row,(1,"red",2))


    def testList(self):
        self.control.add_colour("blue")
        row = self.control.colours()[0]
        self.assertEquals(row,(1,"blue",None))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()