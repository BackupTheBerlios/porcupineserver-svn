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
from msilib.schema import Shortcut
"Porcupine Berkeley DB cursor classes"
import cPickle
from bsddb import db
from threading import currentThread

from porcupine.db import _db
from porcupine.db.basecursor import BaseCursor
from porcupine.security import objectAccess
from porcupine.systemObjects import Shortcut

class Cursor(BaseCursor):
    "BerkeleyDB cursor class"
    def __init__(self, index, txn=None, use_primary=False,
                 fetch_all=False, resolve_shortcuts=False):
        BaseCursor.__init__(self, index, use_primary,
                            fetch_all, resolve_shortcuts)
        self._cursor = self._index.db.cursor(txn)
        self._is_set = False
        self._txn = txn
        
    def set(self, v):
        BaseCursor.set(self, v)
        self._is_set = bool(self._cursor.set(self._value))
    
    def set_range(self, v1, v2):
        BaseCursor.set_range(self, v1, v2)
        self._is_set = bool(self._cursor.set_range(self._range[0]))
    
    def get_both(self, key, value):
        return self._cursor.get_both(cPickle.dumps(key, 2),
                                     cPickle.dumps(value, 2))
    
    def get_current(self):
        if self._primary:
            return self._cusror.pget(db.DB_CURRENT)
        else:
            return self._cursor.current()
    
    def __iter__(self):
        if self._is_set:
            thread = currentThread()
            if self._primary:
                get = self._cursor.pget
            else:
                get = self._cursor.get
            key, value = get(db.DB_CURRENT)
            if self._value:
                # equality
                while key == self._value:
                    if self._primary:
                        yield value
                    else:
                        item = cPickle.loads(value)
                        if self._fetch_all:
                            if self._resolve_shortcuts:
                                while item != None and isinstance(item, Shortcut):
                                    item = _db.getItem(item.target.value,
                                                       self._txn)
                            if item != None:
                                yield item
                        else:
                            # check read permissions
                            access = objectAccess.getAccess(item,
                                                            thread.context.user)
                            if not item._isDeleted and access > 0:
                                if self._resolve_shortcuts and \
                                        isinstance(item, Shortcut):
                                    target = item.get_target(self._txn)
                                    if target:
                                        yield target
                                else:
                                    yield item
                    next = get(db.DB_NEXT)
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
    def __init__(self, primary_db, cursor_list, txn=None, use_primary=False,
                 fetch_all=False, resolve_shortcuts=False):
        self._primary = use_primary
        self._fetch_all = fetch_all
        self._resolve_shortcuts = resolve_shortcuts
        self._thread = currentThread()
        self._txn = txn
        
        self._join = None
        self._get = None
        
        is_natural = True
        should_join = True
        for cur in cursor_list:
            is_natural = (cur._value != None) and is_natural
            should_join = cur._is_set and should_join
        if should_join:
            if is_natural:
                self._join = primary_db.join([c._cursor for c in cursor_list])
                if self._primary:
                    self._get = self._join.join_item
                else:
                    self._get = self._join.get
        
    def next(self):
        if self._get != None:
            next = self._get(0)
            if next != None:
                if self._primary:
                    return next[1]
                else:
                    item = cPickle.loads(next[1])
                    if self._fetch_all:
                        if self._resolve_shortcuts:
                            while item != None and isinstance(item, Shortcut):
                                item = _db.getItem(item.target.value,
                                                   self._txn)
                    else:
                        # check read permissions
                        access = objectAccess.getAccess(item,
                                                        self._thread.context.user)
                        if item._isDeleted or access == 0:
                            item = None
                        elif self._resolve_shortcuts and \
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
        if self._join:
            self._join.close()
