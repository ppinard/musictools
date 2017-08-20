#!/usr/bin/env python
"""
================================================================================
:mod:`ripper` -- Rip a CD
================================================================================

.. module:: ripper
   :synopsis: Rip a CD

.. inheritance-diagram:: ripper

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import os
import sys
import imp
from subprocess import call
import re
import logging
from configparser import ConfigParser

# Third party modules.
import discid

# Local modules.
from musictools.song import Song, Artist
from musictools.utils import unicode_to_ascii, get_release

# Globals and constants variables.
logging.getLogger().setLevel(logging.DEBUG)

def _format(text):
    text = unicode_to_ascii(text)
    text = text.lower()
    text = re.sub("[^a-z0-9()\-\[\]\s]", "", text)
    text = re.sub(r'\W', '_', text)
    text = re.sub('_+', '_', text)
    return text

def _filename(track_title, track_number, ext):
    return "%i_%s.%s" % (track_number, _format(track_title), ext)

def _dirname(album_artist, album_title):
    return os.path.join(_format(album_artist), _format(album_title))

# Parsing configuration
if hasattr(sys, "frozen") or hasattr(sys, "importers") or imp.is_frozen("__main__"):
    main_dir = os.path.dirname(sys.executable)
else:
    main_dir = os.path.dirname(sys.argv[0])

cfgpath = os.path.join(main_dir, 'ripper.cfg')
if not os.path.exists(cfgpath):
    print('Error: No ripper.cfg')
    sys.exit(1)
print('=' * 79)
print('Parsing configuration file: %s ...' % cfgpath)

parser = ConfigParser()
parser.read(cfgpath)

music_dir = parser.get('ripper', 'musicDir')
cdda2wav_path = parser.get('ripper', 'cdda2wavPath')
cdda2wav_args = []
if parser.has_option('ripper', 'cdda2wavArgs'):
    cdda2wav_args = parser.get('ripper', 'cdda2wavArgs').split()
ffmpeg_path = parser.get('ripper', 'ffmpegPath')

print('Music dir: %s' % music_dir)
print('cdda2wav: %s' % cdda2wav_path)
print('cdda2wav args: %s' % cdda2wav_args)
print('ffmpeg: %s' % ffmpeg_path)

# Retrieve information from Musicbrainz
print('-' * 79)
print('Searching Musicbrainz...')

try:
    disc_id = discid.read().id
except Exception as ex:
    print('Error while searching Musicbrainz: %s' % str(ex))
    sys.exit(1)

print('Disc id: %s' % disc_id)

#call([internet_program_path, mbdisc.getSubmissionUrl(disc)])
#sys.exit(1)
try:
    release = get_release(disc_id)
except Exception as ex:
    print(ex)
    sys.exit(1)

# Release information
print('-' * 79)
print('Release found')

album_title = release['title']
print('Album title: %s' % album_title)

album_artist = release['artist-credit-phrase']
print('Album artist: %s' % album_artist)

artists = []
for artist in release['artist-credit']:
    artists.append(Artist(name=artist['artist']['name']))

year = release['date']
print('Album year: %s' % year)

print('=' * 79)

# Track offset for multiple CDs
track_offset = 0
tracks = []
for medium in release['medium-list']:
    if medium['disc-list'][0]['id'] == disc_id:
        tracks = medium['track-list']
        break

    track_offset += medium['track-count']

if not tracks:
    print('Cannot find track information')
    sys.exit(1)

print('Track offset: %i' % track_offset)

# Rip tracks
for track in tracks:
    track_title = track['recording']['title']
    track_position = int(track['position'])
    track_number = track_offset + track_position
    print('Ripping track %i - %s' % (track_number, track_title))

    dirname = os.path.join(music_dir, _dirname(album_artist, album_title))
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    filename = _filename(track_title, track_number, 'wav')
    wav_filepath = os.path.normpath(os.path.join(dirname, filename))

    # cdda2wav
    args = [cdda2wav_path] + cdda2wav_args + \
            ['-s', '-paranoia', '-no-infofile', '-v', 'summary', '-t', str(track_position), wav_filepath]
    logging.debug(' '.join(args))

    retcode = call(args)
    logging.debug('cdda2wav return code: %i', retcode)
    if retcode != 0:
        continue

    # ffmpeg
    mp3_filepath = os.path.splitext(wav_filepath)[0] + '.mp3'
    args = [ffmpeg_path, '-i', wav_filepath, '-vn', '-ar', '44100', '-ac', '2',
            '-ab', '192', '-f', 'mp3', '-y', mp3_filepath]
    logging.debug(' '.join(args))

    retcode = call(args)
    logging.debug('ffmpeg return code: %i', retcode)
    if retcode != 0:
        continue

    # add tags
    song = Song(mp3_filepath)

    song.artists.extend(artists)
    song.albumtitle = album_title
    song.year = year
    song.title = track_title
    song.tracknumber = track_number

    song.save()

    # remove wav
    os.remove(wav_filepath)

    print('-' * 79)
