#!/usr/bin/env python3

import unittest
import os
import glob
import py_compile

import mdstat
from mdstatc import MD_Base

class Compile(unittest.TestCase):

    files = []

    def setUp(self):
        cwd = os.path.dirname(os.path.realpath(__file__))
        self.files = glob.glob("{}/**/*.py".format(cwd), recursive=True)

    def test_compile(self):
        for f in self.files:
            py_compile.compile(f, doraise=True)

class MD(MD_Base, unittest.TestCase):
    
    def get_mdstat(self):
        mdfile = open("data/{}".format(self.testfile), "r")
        data = mdstat.parse_stream(mdfile)
        mdfile.close()
        return data

    def test_ok(self):
        self.testfile = "mdstat.ok"
        self.load()
        self.assertEqual(0, self.determine_state())
        self.testfile = "mdstat.ok.2"
        self.load()
        self.assertEqual(0, self.determine_state())
        self.testfile = "mdstat.ok.3"
        self.load()
        self.assertEqual(0, self.determine_state())

    def test_warn(self):
        self.testfile = "mdstat.warn"
        self.load()
        self.assertEqual(1, self.determine_state())

    def test_error(self):
        self.testfile = "mdstat.error"
        self.load()
        self.assertEqual(2, self.determine_state())
        self.testfile = "mdstat.error.2"
        self.load()
        self.assertEqual(2, self.determine_state())

