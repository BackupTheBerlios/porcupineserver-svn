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
"""
Porcupine server cache implementation.
Used by OQL parser to cache ASTs of most commonly used queries
It should be used as object cache also
"""

class Cache(dict):
    def __init__(self, cache_size):
        self.size = cache_size
        self.__accesslist = []
        
    def __getitem__(self, key):
        self.__accesslist.append(key)
        self.__accesslist.remove(key)
        return self[key]
            
    def __putitem__(self, key, value):
        if len(self.__accesslist) >= self.size:
            del self[self.__accesslist[0]]
            del self.__accesslist[0]
        self[key] = value
        self.__accesslist.append(key)
