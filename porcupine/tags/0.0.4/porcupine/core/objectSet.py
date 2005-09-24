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
Porcupine Object Set
"""

from porcupine.db import db

class ObjectSet(object):
    """
    Porcupine Object Set
    ====================
    The Porcupine object set is a versatile type for keeping a large collection
    of objects or rows with a specified schema.
    It suppports the iterator protocol and partially emulates the list type.
    It implements the C{len} function, membership tests (C{in} operator),
    slices, and the '+' operator.
    """
    def __init__(self, data, schema=None):
        self._list = data
        self.__index = -1

        self.__cache = []
        self.__objectcache = 4000
        self.__cacheindex = 0

        # schema info
        self.schema = schema

    def __iter__(self):
        return self
    
    def __len__(self):
        return len(self._list)
        
    def __add__(self, objectset):
        """Implmements the '+' operator.
        In order to add two object sets successfully one the following
        conditions must be met:
            1. Both of the object sets must contain objects
            2. Object sets must have identical schema
        """
        if self.schema == objectset.schema:
            return ObjectSet(self._list + objectset._list)
        else:
            raise TypeError, 'Unsupported operand (+). Objectsets do not' + \
                ' have the same schema'
        
    def __contains__(self, value):
        """Implements membership tests.
        If the object set contains objects then legal tests are:
            1. C{object_id in objectset}
            2. C{object in objectset}
        If the object set contains rows then legal tests are:
            1. C{row_tuple in objectset}
            2. C{value in objectset} if the object set contains one field
        """
        if self.schema:
            if len(self.schema) != 1:
                return value in self._list
            else:
                return value in [z[0] for z in self._list]
        else:
            if not isinstance(value, str):
                try:
                    value = value._id
                except AttributeError:
                    raise TypeError, 'Invalid argument type'
            return value in self._list

    def __getitem__(self, key):
        """Implements slicing.
        Useful for paging.
        """
        return ObjectSet(self._list[key], self.schema)

    def __loadcache(self, istart):
#        print 'loading cache ' + str(istart)
        self.__cache = [
            db.getItem(id)
            for id in self._list[istart:istart + self.__objectcache]
        ]
        self.__cacheindex = istart

    def next(self):
        self.__index += 1
        if self.__index == len(self._list):
            raise StopIteration
        retVal = self._list[self.__index]
        if not self.schema:
            if isinstance(retVal, str):
                if self.__index > self.__cacheindex + self.__objectcache or \
                            self.__index < self.__cacheindex or \
                            not self.__cache:
                    # we need to load cache
                    self.__loadcache(self.__index)
                return self.__cache.pop(0)
            else:
                return retVal
        else:
            rec = {}
            for i in range(len(self.schema)):
                rec[self.schema[i]] = retVal[i]
            return rec

    