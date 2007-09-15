#===============================================================================
#    Copyright 2005-2007, Tassos Koutsovassilis
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

from porcupine.config import dbparams
from porcupine.db import db
from porcupine.security import inMemorySessionManager
from porcupine.security import sessionManager

def getHandle():
    #open database
    db.open(dbparams.db_class)
    #create in-memory session manager
    sessionManager.open(inMemorySessionManager.SessionManager, 1200)
    oSystemUser = db.getItem('system')
    currentThread().session = sessionManager.create(oSystemUser)
    currentThread().trans = None
    return db

def close():
    sessionManager.close()
    db.close()
    
class OfflineTransaction(object):
    def __init__(self):
        self.actions = []
        self.txn = db.createTransaction()

    def commit(self):
        db.commitTransaction(self.txn)

    def abort(self):
        db.abortTransaction(self.txn)
