#===============================================================================
#    Copyright 2005-2008, Tassos Koutsovassilis
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
"""
Porcupine miscelaneous utilities
"""

import md5, time, random, sys, imp, os

VALID_ID_CHRS = [
    chr(x) for x in \
    range(ord('a'), ord('z')) +
    range(ord('A'), ord('Z')) +
    range(ord('0'), ord('9'))
]

def generateGUID():
    """
    Generates a GUID string.
    
    The GUID length is 32 characters. It is used by the
    session manager to generate session IDs.
    
    @rtype: str
    """
    return md5.new(str(time.time()+time.clock()*1000)).hexdigest()
    
def generateOID():
    """
    Generates an Object ID string.
    
    The generated ID is 8 characters long.
    
    @rtype: str
    """
    return ''.join(random.sample(VALID_ID_CHRS, 8))

def getCallableByName(name):
    """
    This function returns an attribute by name.
    
    For example::
    
        getCallableByName('org.innoscript.desktop.schema.common.Folder')()
    
    instantiates a new I{Folder} object.
        
    @rtype: callable type
    """
    modules = name.split('.')
    if len(modules)==1:
        __module__ = modules[0]
        __attribute__ = []
    else:
        __module__ = '.'.join(modules[:-1])
        __attribute__ = modules[-1]
    
    mod = __import__( __module__, globals(), locals(), __attribute__ )
    if __attribute__:
        attribute = getattr(mod, __attribute__)
        return attribute
    else:
        return mod

def getAddressFromString(address):
    """
    Accepts a string of the form
    C{address:port} and returns an C{(address, port)} tuple.
    
    @param address: string of the form C{address:port}
    @type address: str
    
    @rtype: tuple
    """
    address = address.split(':')
    address[1] = int(address[1])
    return tuple(address)
    
def getFullPath(item):
    """
    Returns the full path of an object
    
    @param item: a Porcupine Object
    @type item: L{GenericItem<porcupine.systemObjects.GenericItem>}
    
    @rtype: str
    """
    parents = item.getAllParents()
    sPath = '/'
    for parent in parents:
        sPath += parent.displayName.value + '/'
    return sPath

