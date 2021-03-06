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
"""This modules provides an offline handle for database access through
the Porcupine API.
"""
from threading import currentThread

from porcupine.db import _db
from porcupine.core.http.context import HttpContext

def getHandle(identity=None):
    #open database
    _db.open()
    if identity==None:
        identity = _db.getItem('system')
    currentThread().context = HttpContext()
    currentThread().context.user = identity
    currentThread().trans = None
    return _db

def close():
    _db.close()
    
class OfflineTransaction(object):
    def __init__(self):
        self.txn = _db.createTransaction()

    def commit(self):
        _db.commitTransaction(self.txn)

    def abort(self):
        _db.abortTransaction(self.txn)
