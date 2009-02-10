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
Porcupine Berkeley DB cursor classes
"""
import cPickle
from bsddb import db
from threading import currentThread

from porcupine.db import _db
from porcupine.db.basecursor import BaseCursor
from porcupine.utils import permsresolver
from porcupine.systemObjects import Shortcut

class Cursor(BaseCursor):
    "BerkeleyDB cursor class"
    def __init__(self, index, txn=None):
        BaseCursor.__init__(self, index)
        self._cursor = self._index.db.cursor(txn)
        self._is_set = False
        self._txn = txn
        self._get_flag = db.DB_NEXT
        
    def set(self, v):
        BaseCursor.set(self, v)
        self._is_set = bool(self._cursor.set(self._value))
    
    def set_range(self, v1, v2):
        BaseCursor.set_range(self, v1, v2)
        self._is_set = bool(self._cursor.set_range(self._range[0]))

    def reverse(self):
        BaseCursor.reverse(self)
        if self._is_set:
            if self._reversed:
                self._get_flag = db.DB_PREV
                self._cursor.get(db.DB_NEXT_NODUP)
                self._cursor.get(db.DB_PREV)
            else:
                self._get_flag = db.DB_NEXT
                self._cursor.set(self._value)

    def get_both(self, key, value):
        return self._cursor.get_both(cPickle.dumps(key, 2),
                                     cPickle.dumps(value, 2))
    
    def get_current(self):
        if self.use_primary:
            return self._cusror.pget(db.DB_CURRENT)
        else:
            return self._cursor.current()
    
    def __iter__(self):
        if self._is_set:
            thread = currentThread()
            if self.use_primary:
                get = self._cursor.pget
            else:
                get = self._cursor.get
            key, value = get(db.DB_CURRENT)
            if self._value:
                # equality
                while key == self._value:
                    if self.use_primary:
                        yield value
                    else:
                        item = cPickle.loads(value)
                        if self.fetch_all:
                            if self.resolve_shortcuts:
                                while item != None and isinstance(item, Shortcut):
                                    item = _db.getItem(item.target.value,
                                                       self._txn)
                            if item != None:
                                yield item
                        else:
                            # check read permissions
                            access = permsresolver.get_access(
                                item,
                                thread.context.user)
                            if not item._isDeleted and access > 0:
                                if self.resolve_shortcuts and \
                                        isinstance(item, Shortcut):
                                    target = item.get_target(self._txn)
                                    if target:
                                        yield target
                                else:
                                    yield item
                    next = get(self._get_flag)
                    if not next:
                        break
                    key, value = next
            else:
                # range
                raise NotImplementedError            
    
    def close(self):
        self._cursor.close()

class Join(object):
    "Helper cursor for performing joins"
    def __init__(self, primary_db, cursor_list, txn=None):
        self._thread = currentThread()
        self._txn = txn
        self._cur_list = cursor_list
        self._join = None
        self._is_set = True

        self.use_primary = False
        self.fetch_all = False
        self.resolve_shortcuts = False

        is_natural = True
        for cur in self._cur_list:
            is_natural = (cur._value != None) and is_natural
            self._is_set = cur._is_set and self._is_set
        if self._is_set:
            if is_natural:
                self._join = primary_db.join([c._cursor
                                              for c in self._cur_list])
    
    def next(self):
        if self._is_set:
            if self._join != None:
                if self.use_primary:
                    get = self._join.join_item
                else:
                    get = self._join.get

                next = get(0)
                if next != None:
                    if self.use_primary:
                        return next
                    else:
                        item = cPickle.loads(next[1])
                        if self.fetch_all:
                            if self.resolve_shortcuts:
                                while item != None and isinstance(item,
                                                                  Shortcut):
                                    item = _db.getItem(item.target.value,
                                                       self._txn)
                        else:
                            # check read permissions
                            access = permsresolver.get_access(
                                item,
                                self._thread.context.user)
                            if item._isDeleted or access == 0:
                                item = None
                            elif self.resolve_shortcuts and \
                                    isinstance(item, Shortcut):
                                item = item.get_target(self._txn)

                        if item != None:
                            return item
                        else:
                            return self.next()
    
    def __iter__(self):
        next = self.next()
        while next:
            yield next
            next = self.next()
    
    def close(self):
        [cur.close() for cur in self._cur_list]
        if self._join:
            self._join.close()
