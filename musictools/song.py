#!/usr/bin/env python
"""
================================================================================
:mod:`song` -- Reader and writer of MP3, WMA and OGG metadata
================================================================================

.. module:: song
   :synopsis: Reader and writer of MP3, WMA and OGG metadata

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2010 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os.path
import warnings

# Third party modules.
import mutagen.id3 as id3
import mutagen.oggvorbis as ogg

# Local modules.

# Globals and constants variables.
EXTENSION_MP3 = 'mp3'
EXTENSION_OGG = 'ogg'

class Artist(object):

    def __init__(self, name=None, firstname=None, lastname=None):
        if name is not None:
            firstname, lastname = self._split_name(name)

        self._firstname = firstname.strip()
        self._lastname = lastname.strip()

    def __repr__(self):
        return self.name

    def _split_name(self, name):
        name = name.strip()
        names = name.split(' ')
        firstname = ' '.join(names[:-1])
        lastname = names[-1]

        return firstname, lastname

    @property
    def firstname(self):
        return self._firstname

    @property
    def lastname(self):
        return self._lastname

    @property
    def name(self):
        name = []
        if len(self._firstname) > 0:
            name.append(self._firstname)

        if len(self._lastname) > 0:
            name.append(self._lastname)

        return ' '.join(name)

    def __eq__(self, other):
        equality = True

        equality = equality and self._firstname == other._firstname
        equality = equality and self._lastname == other._lastname

        return equality

    def __ne__(self, other):
        return not self == other

class Song(object):
    def __init__(self, filepath):
        self.filepath = filepath
        _root, extension = os.path.splitext(filepath)

        # Reset
        del self.artists
        del self.albumtitle
        del self.title
        del self.tracknumber
        del self.description
        del self.year
        del self.genre

        if extension == '.' + EXTENSION_MP3:
            self._filetype = EXTENSION_MP3
            self._read_mp3(filepath)
        elif extension == '.' + EXTENSION_OGG:
            self._filetype = EXTENSION_OGG
            self._read_ogg(filepath)
        else:
            raise IOError("Invalid extension (%s)" % extension)

    def __repr__(self):
        artists = ','.join(self.artists)
        return "%i - %s - %s (%i) by %s" % \
            (self.tracknumber, self.title, self.albumtitle, self.year, artists)

    def _read_mp3(self, filepath):
        mp3info = id3.ID3(filepath)

        for code in ['TPE1', 'TPE2', 'TPE3', 'TPE4']:
            author = mp3info.get(code)
            if author is not None:
                artist = Artist(name=author.text[0])
                self.artists.append(artist)
        if self.artists:
            self.primary_artist = self.artists[0]

        title = mp3info.get('TIT2', mp3info.get('TIT1'))
        if title is not None:
            self.title = title.text[0]
        else:
            warnings.warn("Song (%s) does not have a title." % filepath)

        albumtitle = mp3info.get('TALB')
        if albumtitle is not None:
            self.albumtitle = albumtitle.text[0]
        else:
            warnings.warn("Song (%s) does not have an album title." % filepath)

        tracknumber = mp3info.get('TRCK')
        if tracknumber is not None:
            self.tracknumber = tracknumber.text[0].split('/')[0]
        else:
            warnings.warn("Song (%s) does not have a track number." % filepath)

#        description = mp3info.get('TIT2')
#        if description is not None: description = description.text[0]
#        self.set_description(description)

        year = mp3info.get('TYER', mp3info.get('TDRC'))
        if year is not None:
            self.year = str(year.text[0])
        else:
            warnings.warn("Song (%s) does not have a year." % filepath)

        genre = mp3info.get('TCON')
        if genre is not None:
            self.genre = genre.text[0]
        else:
            warnings.warn("Song (%s) does not have a genre." % filepath)

    def _read_ogg(self, filepath):
        ogginfo = ogg.OggVorbis(filepath)

        authors = ogginfo.get('artist')
        for author in authors:
            artist = Artist(author)
            self.artists.append(artist)

        title = ogginfo.get('title')
        if title is not None:
            self.title = title[0]
        else:
            warnings.warn("Song (%s) does not have a title." % filepath)

        albumtitle = ogginfo.get('album')
        if albumtitle is not None:
            self.albumtitle = albumtitle[0]
        else:
            warnings.warn("Song (%s) does not have an album title." % filepath)

        tracknumber = ogginfo.get('tracknumber')
        if tracknumber is not None:
            self.tracknumber = tracknumber[0]
        else:
            warnings.warn("Song (%s) does not have a track number." % filepath)

#        description = ogginfo.get('description')
#        if description is not None:
#            description = description[0]
#        else:
#            description = ''
#        self.set_description(description)

        year = ogginfo.get('date')
        if year is not None:
            self.year = year[0]
        else:
            warnings.warn("Song (%s) does not have a year." % filepath)

        genre = ogginfo.get('genre')
        if genre is not None:
            self.genre = genre[0]
        else:
            warnings.warn("Song (%s) does not have a genre." % filepath)

    @property
    def filepath(self):
        """
        The filepath of the song.
        """
        return self._filepath

    @filepath.setter
    def filepath(self, filepath):
        assert os.path.exists(filepath)
        self._filepath = filepath

    @property
    def filetype(self):
        """
        Extension of the filepath.
        """
        _root, extension = os.path.splitext(self.filepath)
        return extension[1:]

    @property
    def artists(self):
        """
        The song's artists.
        :rtype: list
        """
        return self._artists

    @artists.deleter
    def artists(self):
        self._artists = []

    @property
    def albumtitle(self):
        """
        The album's title.
        """
        return self._albumtitle

    @albumtitle.setter
    def albumtitle(self, albumtitle):
        self._albumtitle = albumtitle

    @albumtitle.deleter
    def albumtitle(self):
        self._albumtitle = ""

    @property
    def title(self):
        """
        The song's title.
        """
        return self._title

    @title.setter
    def title(self, title):
        self._title = title

    @title.deleter
    def title(self):
        self._title = ""

    @property
    def tracknumber(self):
        """
        The song's track number.
        """
        return self._tracknumber

    @tracknumber.setter
    def tracknumber(self, tracknumber):
        self._tracknumber = int(tracknumber)

    @tracknumber.deleter
    def tracknumber(self):
        self._tracknumber = 0

    @property
    def description(self):
        """
        The song's description.
        """
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @description.deleter
    def description(self):
        self._description = ""

    @property
    def year(self):
        """
        The song's year
        """
        return self._year

    @year.setter
    def year(self, year):
        self._year = int(str(year))

    @year.deleter
    def year(self):
        self._year = 0

    @property
    def genre(self):
        """
        The song's genre
        """
        return self._genre

    @genre.setter
    def genre(self, genre):
        self._genre = str(genre)

    @genre.deleter
    def genre(self):
        self._genre = "Unknown"

    def save(self):
        """
        Saves the information to the current file or new file.
        """
        if self.filetype == EXTENSION_MP3:
            self._save_mp3(self.filepath)
        elif self.filetype == EXTENSION_OGG:
            self._save_ogg(self.filepath)
        else:
            raise IOError("Invalid extension (%s)" % self.filetype)

    def _save_mp3(self, filepath):
        mp3info = id3.ID3(filepath)

        if len(self.artists) >= 1:
            text = id3.TPE1(encoding=3, text=[self.artists[0]])
            mp3info['TPE1'] = text
        if len(self.artists) >= 2:
            text = id3.TPE2(encoding=3, text=[self.artists[1]])
            mp3info['TPE2'] = text
        if len(self.artists) >= 3:
            text = id3.TPE3(encoding=3, text=[self.artists[2]])
            mp3info['TPE3'] = text
        if len(self.artists) >= 4:
            text = id3.TPE4(encoding=3, text=[self.artists[3]])
            mp3info['TPE4'] = text

        TIT2 = id3.TIT2(encoding=3, text=self.title)
        mp3info['TIT2'] = TIT2

        TALB = id3.TALB(encoding=3, text=self.albumtitle)
        mp3info['TALB'] = TALB

        TRCK = id3.TRCK(encoding=3, text=str(self.tracknumber))
        mp3info['TRCK'] = TRCK

        TIT3 = id3.TIT3(encoding=3, text=self.description)
        mp3info['TIT3'] = TIT3

        if self.year == 0:
            year = '0000'
        else:
            year = str(self.year)
        TYER = id3.TYER(encoding=3, text=str(year))
        TDRC = id3.TDRC(encoding=3, text=str(year))
        mp3info['TYER'] = TYER
        mp3info['TDRC'] = TDRC

        TCON = id3.TCON(encoding=3, text=self.genre)
        mp3info['TCON'] = TCON

        mp3info.save(filepath)

    def _save_ogg(self, filepath):
        ogginfo = ogg.OggVorbis(filepath)

        ogginfo['artist'] = [str(artist) for artist in self.artists]

        ogginfo['title'] = [self.title]

        ogginfo['album'] = [self.albumtitle]

        ogginfo['tracknumber'] = [str(self.tracknumber)]

        ogginfo['description'] = [self.description]

        if self.year == 0:
            year = '0000'
        else:
            year = str(self.year)
        ogginfo['date'] = [year]

        ogginfo['genre'] = [self.genre]

        ogginfo.save(filepath)
