#!/usr/bin/env python
"""
================================================================================
:mod:`song` -- Reader and writer of MP3, WMA and OGG metadata
================================================================================

.. module:: song
   :synopsis: Reader and writer of MP3, WMA and OGG metadata

"""

# Standard library modules.
import os
import re
import warnings

# Third party modules.
import mutagen.id3 as id3
import mutagen.oggvorbis as ogg

# Local modules.
from musictools.utils import unicode_to_ascii

# Globals and constants variables.
EXTENSION_MP3 = 'mp3'
EXTENSION_OGG = 'ogg'

def _format(text):
    text = unicode_to_ascii(text)
    text = text.lower()
    text = re.sub("[^a-z0-9()\-\[\]\s]", "", text)
    text = re.sub(r'\W', '_', text)
    text = re.sub('_+', '_', text)
    text = text.rstrip('_')
    return text

class Artist(object):

    def __init__(self, name=None, firstname=None, lastname=None):
        if name is not None:
            firstname, lastname = self._split_name(name)

        self._firstname = firstname.strip()
        self._lastname = lastname.strip()

    def __repr__(self):
        return '<Artist({})>'.format(self.name)

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
        return self._firstname == other._firstname and self._lastname == other._lastname

    def __hash__(self):
        return hash((self.__class__, self._firstname, self._lastname))

class Song(object):

    def __init__(self, filepath):
        self.filepath = filepath
        _root, extension = os.path.splitext(filepath)

        # Reset
        self.artists = []
        self.albumtitle = ''
        self.title = ''
        self.tracknumber = 0
        self.description = ''
        self.year = 0
        self.genre = ''
        self.discnumber = 0

        if extension == '.' + EXTENSION_MP3:
            self.filetype = EXTENSION_MP3
            self._read_mp3(filepath)
        elif extension == '.' + EXTENSION_OGG:
            self.filetype = EXTENSION_OGG
            self._read_ogg(filepath)
        else:
            raise IOError("Invalid extension (%s)" % extension)

    def __repr__(self):
        artists = ','.join(self.artists)
        return "<Song(%i - %s - %s (%i) by %s)>" % \
            (self.tracknumber, self.title, self.albumtitle, self.year, artists)

    def _read_mp3(self, filepath):
        mp3info = id3.ID3(filepath)

        for code in ['TPE1', 'TPE2', 'TPE3', 'TPE4']:
            author = mp3info.get(code)
            if not author:
                continue
            if not author.text[0]:
                continue

            artist = Artist(name=author.text[0])

            if artist not in self.artists:
                self.artists.append(artist)

        title = mp3info.get('TIT2', mp3info.get('TIT1'))
        if title is not None:
            self.title = str(title.text[0])
        else:
            warnings.warn("Song (%s) does not have a title." % filepath)

        albumtitle = mp3info.get('TALB')
        if albumtitle is not None:
            self.albumtitle = str(albumtitle.text[0])
        else:
            warnings.warn("Song (%s) does not have an album title." % filepath)

        tracknumber = mp3info.get('TRCK')
        if tracknumber is not None:
            self.tracknumber = int(tracknumber.text[0].split('/')[0])
        else:
            warnings.warn("Song (%s) does not have a track number." % filepath)

#        description = mp3info.get('TIT2')
#        if description is not None: description = description.text[0]
#        self.set_description(description)

        year = mp3info.get('TYER', mp3info.get('TDRC'))
        if year is not None:
            self.year = int(str(year.text[0]))
        else:
            warnings.warn("Song (%s) does not have a year." % filepath)

        genre = mp3info.get('TCON')
        if genre is not None:
            self.genre = genre.text[0]
        else:
            warnings.warn("Song (%s) does not have a genre." % filepath)

        disc = mp3info.get('TPOS')
        if disc is not None:
            discnumber, total = map(int, disc.text[0].split('/'))
            self.discnumber = discnumber if total >= 2 else 0
        else:
            warnings.warn("Song (%s) does not have a disc number." % filepath)

    def _read_ogg(self, filepath):
        ogginfo = ogg.OggVorbis(filepath)

        authors = ogginfo.get('artist')
        for author in authors:
            artist = Artist(author)
            if artist not in self.artists:
                self.artists.append(artist)

        title = ogginfo.get('title')
        if title is not None:
            self.title = str(title[0])
        else:
            warnings.warn("Song (%s) does not have a title." % filepath)

        albumtitle = ogginfo.get('album')
        if albumtitle is not None:
            self.albumtitle = str(albumtitle[0])
        else:
            warnings.warn("Song (%s) does not have an album title." % filepath)

        tracknumber = ogginfo.get('tracknumber')
        if tracknumber is not None:
            self.tracknumber = int(tracknumber[0])
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
            self.year = int(year[0])
        else:
            warnings.warn("Song (%s) does not have a year." % filepath)

        genre = ogginfo.get('genre')
        if genre is not None:
            self.genre = genre[0]
        else:
            warnings.warn("Song (%s) does not have a genre." % filepath)

    @property
    def formatted_filename(self):
        if self.discnumber != 0:
            return "{:02d}-{:02d}_{}.{}".format(self.discnumber, self.tracknumber,
                                                _format(self.title), self.filetype)
        else:
            return "{:02d}_{}.{}".format(self.tracknumber, _format(self.title), self.filetype)

    @property
    def formatted_dirname(self):
        return os.path.join(_format(self.artists[0].name), _format(self.albumtitle))

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
            text = id3.TPE1(encoding=3, text=[self.artists[0].name])
            mp3info['TPE1'] = text
        if len(self.artists) >= 2:
            text = id3.TPE2(encoding=3, text=[self.artists[1].name])
            mp3info['TPE2'] = text
        if len(self.artists) >= 3:
            text = id3.TPE3(encoding=3, text=[self.artists[2].name])
            mp3info['TPE3'] = text
        if len(self.artists) >= 4:
            text = id3.TPE4(encoding=3, text=[self.artists[3].name])
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

        ogginfo['artist'] = [artist.name for artist in self.artists]

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
