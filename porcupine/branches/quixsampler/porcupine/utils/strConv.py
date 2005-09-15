#===============================================================================
#    Copyright 2005, Tassos Koutsovassilis
#
#    This file is part of Porcupine.
#    Porcupine is free software; you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation; either version 2.1 of the License, or
#    (at your option) any later version.
#    Porcupine is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#    You should have received a copy of the GNU Lesser General Public License
#    along with Porcupine; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#===============================================================================
"Character encoding conversion utilities"

def ansiToUnicode(sString, sEnc):
    return(unicode(sString, sEnc))

def unicodeToAscii(sString):
    return(sString.encode('iso-8859-1'))

def ansiToUtf8(sString, sEnc):
    return(unicodeToUtf8(ansiToUnicode(sString, sEnc)))

def utf8ToAnsi(sString):
    return(sString.encode('iso-8859-1'))

def unicodeToUtf8(sString):
    return(sString.encode('utf-8'))

def utf8ToUnicode(sString):
    return(unicode(sString, 'utf-8'))