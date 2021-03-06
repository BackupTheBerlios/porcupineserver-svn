#===============================================================================
#    Copyright 2005-2009, Tassos Koutsovassilis
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
"Base database index class"
import cPickle

from porcupine.core import persist, cache

_cache = cache.Cache(20)

class BaseIndex(object):
    def __init__(self, name, unique):
        self.unique = unique
        self.name = name
        self.callback = self._get_callback()
    
    def _get_callback(self):
        def callback(key, value):
            item = _cache.get(value, persist.loads(value))
            index_value = None
            if hasattr(item, self.name):
                attr = getattr(item, self.name)
                if attr.__class__.__module__ != '__builtin__':
                    attr = attr.value
                index_value = cPickle.dumps(attr, 2)
            _cache[value] = item
            return index_value
        return callback
    
    def close(self):
        raise NotImplementedError
