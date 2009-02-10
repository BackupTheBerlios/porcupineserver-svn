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
"Base database cursor class"
import cPickle

class BaseCursor(object):
    def __init__(self, index):
        self._index = index
        self._value = None
        self._range = []
        self._reversed = False

        self.use_primary = False
        self.fetch_all = False
        self.resolve_shortcuts = False

    def set(self, v):
        val = cPickle.dumps(v, 2)
        self._value = val
        self._range = []
    
    def set_range(self, v1, v2):
        self._range = []
        if v1 != None:
            val1 = cPickle.dumps(v1, 2)
            self._range.append(val1)
        else:
            self._range.append('')
        if v2 != None:
            val2 = cPickle.dumps(v2, 2)
            self._range.append(val2)
        else:
            self._range.append(None)

    def reverse(self):
        self._reversed = not self._reversed
    
    def get_current(self):
        raise NotImplementedError
    
    def get_both(self, key, value):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError
    
    def close(self):
        raise NotImplementedError
