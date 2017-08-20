#!/usr/bin/env python
""" """

# Standard library modules.
import unittest
import logging

# Third party modules.

# Local modules.
from musictools.utils import unicode_to_ascii, get_release

# Globals and constants variables.

class TestUtils(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testunicode_to_ascii(self):
        self.assertEqual(unicode_to_ascii(u'\xe9cole'), 'ecole')
        self.assertEqual(unicode_to_ascii(u'bi\xe8re'), 'biere')
        self.assertEqual(unicode_to_ascii(u'h\xf4pital'), 'hopital')
        self.assertEqual(unicode_to_ascii(u'f\xeate de no\xebl'), 'fete de noel')

    def testget_release(self):
        release = get_release('ubhYGAMKtirc0PWBn6z.MjPkIgU-')
        self.assertEqual('Used to Be Duke', release['title'])

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()
