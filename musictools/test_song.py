#!/usr/bin/env python
"""
================================================================================
:mod:`test_song` -- Unit tests for the module :mod:`song`.
================================================================================

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import unittest
import logging
import shutil
import os

# Third party modules.

# Local modules.
from musictools.song import Song, Artist

# Globals and constants variables.

class TestArtist(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.artist1 = Artist(name='John Doe')
        self.artist2 = Artist(firstname='John', lastname='Doe')

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testSkeleton(self):
        #self.fail("Test if the TestCase is working.")
        self.assertTrue(True)

    def testfirstname(self):
        self.assertEqual(self.artist1.firstname, 'John')
        self.assertEqual(self.artist2.firstname, 'John')

    def testlastname(self):
        self.assertEqual(self.artist1.lastname, 'Doe')
        self.assertEqual(self.artist2.lastname, 'Doe')

    def test__eq__(self):
        self.assertTrue(self.artist1 == self.artist2)

    def test__ne__(self):
        artist = Artist(name='John John')
        self.assertTrue(self.artist1 != artist)

class TestSong(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.folderpath = os.path.join(os.path.dirname(__file__), "testData")
        self.song1_filepath = os.path.join(self.folderpath, 'song.mp3')
        self.song2_filepath = os.path.join(self.folderpath, 'song3.ogg')

        self.song1 = Song(self.song1_filepath)
        self.song2 = Song(self.song2_filepath)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def testfilepath_setter(self):
        self.song1.filepath = self.song2_filepath
        self.assertEqual(self.song1.filepath, self.song2_filepath)

    def testfilepath_getter(self):
        self.assertEqual(self.song1.filepath, self.song1_filepath)
        self.assertEqual(self.song2.filepath, self.song2_filepath)

    def testartists_getter(self):
        self.assertEqual(self.song1.artists,
                         [Artist(name=u'piman')])
        self.assertEqual(self.song2.artists,
                         [Artist(name=u'K.D. Lang'),
                          Artist(name=u'Tony Bennett')])

    def testalbumtitle_setter(self):
        albumtitle = 'abc'
        self.song1.albumtitle = albumtitle
        self.assertEqual(self.song1.albumtitle, albumtitle)

    def testget_albumtitle(self):
        self.assertEqual(self.song1.albumtitle, u'Quod Libet Test Data')
        self.assertEqual(self.song2.albumtitle, u'A Wonderful World')

    def testtitle_setter(self):
        title = 'abc'
        self.song1.title = title
        self.assertEqual(self.song1.title, title)

    def testtitle_getter(self):
        self.assertEqual(self.song1.title, u'Silence')
        self.assertEqual(self.song2.title, u'What a Wonderful World')

    def testtracknumber_setter(self):
        tracknumber = 10
        self.song1.tracknumber = tracknumber
        self.assertEqual(self.song1.tracknumber, 10)

    def testtracknumber_getter(self):
        self.assertEqual(self.song1.tracknumber, 2)
        self.assertEqual(self.song2.tracknumber, 5)

#    def testdescription_setter(self):
#        description = 'abc'
#        self.song1.description = description
#        self.assertEqual(self.song1.description, description)
#
#    def testdescription_getter(self):
#        self.assertEqual(self.song1.description, '')
#        self.assertEqual(self.song2.description, '')
#        self.assertEqual(self.song3.description, '')
#        self.assertEqual(self.song4.description, u'Silence')
#        self.assertEqual(self.song5.description, '')

    def testyear_setter(self):
        year = 2009
        self.song1.year = year
        self.assertEqual(self.song1.year, year)

    def testyear_getter(self):
        self.assertEqual(self.song1.year, 2004)
        self.assertEqual(self.song2.year, 2002)

    def testgenre_setter(self):
        genre = 'Other'
        self.song1.genre = genre
        self.assertEqual(self.song1.genre, genre)

    def testgenre_getter(self):
        self.assertEqual(self.song1.genre, 'Silence')
        self.assertEqual(self.song2.genre, 'Vocal')

    def _build_song(self, filepath):
        song = Song(filepath)

        song.albumtitle = 'abc'
        del song.artists
        song.artists.extend([Artist(name='a'), Artist(name='b'),
                             Artist(name='c'), Artist(name='d')])
        song.description = 'def'
        song.genre = 'Other'
        song.title = 'ghi'
        song.tracknumber = 10
        song.year = 2009

        return song

    def testsave_mp3(self):
        testfilepath = os.path.join(self.folderpath, 'test.mp3')
        shutil.copy(self.song1_filepath, testfilepath)
        song = self._build_song(testfilepath)
        song.save()

        songTest = Song(testfilepath)
        self.assertEqual(songTest.albumtitle, 'abc')
        self.assertEqual(songTest.artists, [Artist(name='a'), Artist(name='b'),
                                            Artist(name='c'), Artist(name='d')])
#        self.assertEqual(songTest.description, 'def')
        self.assertEqual(songTest.genre, 'Other')
        self.assertEqual(songTest.title, 'ghi')
        self.assertEqual(songTest.tracknumber, 10)
        self.assertEqual(songTest.year, 2009)

        os.remove(testfilepath)

    def testsave_ogg(self):
        testfilepath = os.path.join(self.folderpath, 'test.ogg')
        shutil.copy(self.song2_filepath, testfilepath)
        song = self._build_song(testfilepath)
        song.save()

        songTest = Song(testfilepath)
        self.assertEqual(songTest.albumtitle, 'abc')
        self.assertEqual(songTest.artists, [Artist(name='a'), Artist(name='b'),
                                            Artist(name='c'), Artist(name='d')])
#        self.assertEqual(songTest.description, 'def')
        self.assertEqual(songTest.genre, 'Other')
        self.assertEqual(songTest.title, 'ghi')
        self.assertEqual(songTest.tracknumber, 10)
        self.assertEqual(songTest.year, 2009)

        os.remove(testfilepath)

if __name__ == '__main__': #pragma: no cover
    logging.getLogger().setLevel(logging.DEBUG)
    unittest.main()


