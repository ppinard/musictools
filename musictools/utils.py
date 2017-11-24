#!/usr/bin/env python
"""
================================================================================
:mod:`utils` -- Miscellaneous utilities
================================================================================

.. module:: utils
   :synopsis: Miscellaneous utilities

.. inheritance-diagram:: musictools.utils

"""

# Script information for the file.
__author__ = "Philippe T. Pinard"
__email__ = "philippe.pinard@gmail.com"
__version__ = "0.1"
__copyright__ = "Copyright (c) 2011 Philippe T. Pinard"
__license__ = "GPL v3"

# Standard library modules.
import logging
import unicodedata

# Third party modules.
import musicbrainzngs
musicbrainzngs.set_useragent("musictools", "0.1")

# Local modules.

# Globals and constants variables.

def unicode_to_ascii(unistr):
    """
    Convert a unicode string into an ascii string
    by finding the corresponding ascii character for all unicode character.
    
    :arg unistr: unicode string
    :type unistr: :keyword:`unicode`
    """
    ascii_chrs = []

    for char in unistr:
        try:
            char.encode('ascii')
        except UnicodeEncodeError:
            decomposition = unicodedata.decomposition(char)

            if not decomposition: # no decomposition
                continue

            root, *_modifier = decomposition.split()
            try:
                char = chr(int(root, 16)) #root is in hex base
            except:
                continue

        ascii_chrs.append(char)

    return str(''.join(ascii_chrs))

def get_release(discid):
    """
    Returns a Musicbrainz disc object from the current CD.
    
    """
    # Query for all discs matching the given DiscID.
    result = musicbrainzngs.get_releases_by_discid(discid)
    releases = result['disc']['release-list']

    logging.debug("Found %i releases", len(releases))

    # Select the higher score release
    release_id = releases[-1]['id']

    # The returned release object only contains title and artist, but no tracks.
    # Query the web service once again to get all data we need.
    includes = ['artists', 'recordings', 'discids']
    result = musicbrainzngs.get_release_by_id(release_id, includes=includes)

    return result['release']

def unknown_disc_url(disc):
    """
    Returns the HTTP URL to create a new entry in the Musicbrainz database of
    an unknown disc.
    
    :arg disc: disc object from Musicbrainz
    """
    l = [disc.firstTrackNum, disc.lastTrackNum, disc.sectors]
    l += [offset for offset, _length in disc.tracks]
    toc = '+'.join(map(str, l))

    return 'http://musicbrainz.org/cdtoc/attach?id=%s&tracks=%i&toc=%s' % \
        (disc.id, len(disc.tracks), toc)
