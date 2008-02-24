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
Porcupine Object Set
"""
import types

from porcupine import exceptions
from porcupine.db import db
from porcupine.db import dbEnv

class ObjectSet(object):
    """
    Porcupine Object Set
    ====================
    The Porcupine object set is a versatile type for keeping a large collection
    of objects or rows with a specified schema.
    There are two types of object sets; resolved and unresolved. They both
    implement the iterator protocol and the '+' operator.
    
    An unresolved object set may contain references to objects that are not
    accessible given the current security context. Such kind of object sets
    are returned from methods such as:
    L{getChildren<porcupine.systemObjects.Container.getChildren>} and
    L{getItems<porcupine.datatypes.ReferenceN.getItems>}.
    
    The OQL C{select} statement always returns resolved object sets. Resolved
    object sets provide enhanced functionality as they partialy emulate
    the list type. They provide the C{len} function, membership tests
    (C{in} operator) and slicing.
    """
    _cachesize = 100
    def __init__(self,data, schema=None, txn=None,
                 resolved=True, safe=True):
        self.__cache = []

        self._list = data
        self._txn = txn
        self._resolved = resolved
        self._safe = safe

        # schema info
        self.schema = schema

    def __iter__(self):
        if len(self._list) > 0:
            if self.schema == None:
                    if type(self._list[0]) == types.StringType:
                        for x in range(len(self._list))[::self._cachesize]:
                            self.__loadcache(x)
                            while len(self.__cache) > 0:
                                yield self.__cache.pop(0)
                    else:
                        for x in self._list:
                            yield x
            else:
                for x in self._list:
                    yield dict(zip(self.schema, x))
    
    def __len__(self):
        """Returns the size of the objects set.
        Valid only for resolved object sets.
        
        @raise TypeError: if the object set is unresloved
        """
        if self._resolved:
            return len(self._list)
        else:
            raise TypeError, 'unresolved object sets are unsized'
        
    def __add__(self, objectset):
        """Implements the '+' operator.
        In order to add two object sets successfully the objects sets must
        share the same transaction handle and one of the following
        conditions must be met:
            1. Both of the object sets must contain objects
            2. Object sets must have identical schema
        """
        if self.schema == objectset.schema:
            if self._txn == objectset._txn:
                return ObjectSet(self._list + objectset._list,
                                 schema = self.schema,
                                 txn = self._txn,
                                 resolved = self._resolved and
                                            objectset._resolved,
                                 safe = self._safe and
                                          objectset._safe)
            else:
                raise TypeError, 'Unsupported operand (+). Object sets ' + \
                                 'do not share the same transaction'
        else:
            raise TypeError, 'Unsupported operand (+). Object sets do not ' + \
                             'have the same schema'
        
    def __contains__(self, value):
        """Implements membership tests. Valid only for resolved object sets.
        If the object set contains objects then legal tests are:
            1. C{object_id in objectset}
            2. C{object in objectset}
        If the object set contains rows then legal tests are:
            1. C{row_tuple in objectset}
            2. C{value in objectset} if the object set contains one field
            
        @raise TypeError: if the object set is unresloved
        """
        if self._resolved:
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
        else:
            raise TypeError, 'unresolved object sets do not support ' + \
                             'membership tests'

    def __getitem__(self, key):
        """Implements slicing. Valid only for resolved object sets.
        Useful for paging.
        
        @raise TypeError: if the object set is unresloved
        """
        if self._resolved:
            return ObjectSet(self._list[key],
                             schema = self.schema,
                             txn = self._txn)
        else:
            raise TypeError, 'unresolved object sets do not support slicing'
        
    def __getItemSafe(self, id):
        try:
            return dbEnv.getItem(id, self._txn)
        except exceptions.ObjectNotFound:
            return None

    def __loadcache(self, istart):
        if self._resolved:
            self.__cache = [
                db.getItem(id, self._txn)
                for id in self._list[istart:istart + self._cachesize]]
        else:
            if self._safe:
                self.__cache = filter(None,
                    [dbEnv.getItem(id, self._txn)
                     for id in self._list[istart:istart + self._cachesize]])
            else:
                self.__cache = filter(None,
                    [self.__getItemSafe(id)
                     for id in self._list[istart:istart + self._cachesize]])
