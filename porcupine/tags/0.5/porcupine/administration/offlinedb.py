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
Porcupine API.
"""

from threading import currentThread

from porcupine.config.settings import settings
from porcupine.utils import misc
from porcupine.db import _db

from porcupine.core.http.context import HttpContext
from porcupine.security import inMemorySessionManager
from porcupine.security import SessionManager

def getHandle():
    #open database
    _db.open(misc.getCallableByName(settings['store']['interface']))
    #create in-memory session manager
    SessionManager.open(inMemorySessionManager.SessionManager, 1200)
    oSystemUser = _db.getItem('system')
    context = HttpContext()
    context.session = SessionManager.create(oSystemUser)
    
    currentThread().context = context
    currentThread().trans = None
    return _db

def close():
    SessionManager.close()
    _db.close()
    
class OfflineTransaction(object):
    def __init__(self):
        self.actions = []
        self.txn = _db.createTransaction()

    def commit(self):
        _db.commitTransaction(self.txn)

    def abort(self):
        _db.abortTransaction(self.txn)
