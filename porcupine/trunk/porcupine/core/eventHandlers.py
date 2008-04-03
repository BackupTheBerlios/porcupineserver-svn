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
"Porcupine server event handlers base classes"
from porcupine import db
from porcupine.db import _db

class DatatypeEventHandler(object):
    db = _db
    store = db

    @classmethod
    def on_create(cls, item, attr, trans):
        pass

    @classmethod
    def on_update(cls, item, new_attr, old_attr, trans):
        pass
    
    @classmethod
    def on_delete(cls, item, attr, trans, bPermanent):
        pass
    
class ContentclassEventHandler(object):
    store = db
    
    @classmethod
    def on_create(cls, item, trans):
        pass
    
    @classmethod
    def on_update(cls, item, old_item, trans):
        pass
    
    @classmethod
    def on_delete(cls, item, trans, bPermanent):
        pass
