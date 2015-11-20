# THIS FILE IS GENERATED FROM THE SETUP.PY. DO NOT EDIT.
"""Audiolab is a python package for audio file IO using numpy arrays. It supports
many different audio formats, including wav, aiff, au, flac, ogg, htk. It also
supports output to audio device (Mac OS X and Linux only).

For simplicity, a matlab-like API is provided for simple import/export; a more
complete API is also available.

Audiolab is essentially a wrapper around Erik de Castro Lopo's excellent
libsndfile:

http://www.mega-nerd.com/libsndfile/

LICENSE: audiolab is licensed under the LGPL, as is libsndfile itself. See
COPYING.txt for details.  

2006-2008, David Cournapeau
"""
# version of the python module (compatibility -> use
# scikits.samplerate.version.version instead, to be consistent with numpy)
from version import short_version as version
ignore  = False