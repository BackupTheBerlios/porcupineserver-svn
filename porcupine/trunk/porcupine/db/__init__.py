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
Porcupine database package
"""
from threading import currentThread

from porcupine.db import _db
from porcupine import exceptions
from porcupine.security import objectAccess

def getItem(sPath, trans=None):
    """
    Fetches an object from the database. If the user has no read permissions
    on the object then C{None} is returned.
    
    @param sPath: The object's ID or the object's full path.
    @type sPath: str
    
    @param trans: A valid transaction handle.
    
    @rtype: L{GenericItem<porcupine.systemObjects.GenericItem>}
    
    @raise porcupine.exceptions.ObjectNotFound: if the item does
           not exist
    """
    if (trans):
        trans.actions.append( (getItem, (sPath, trans)) )
    try:
        oItem = _db.getItem(sPath, trans)
    except exceptions.DBTransactionIncomplete:
        trans.retry()
    # check read permissions
    if objectAccess.getAccess(oItem, currentThread().context.session.user) != 0:
        return oItem
    else:
        return None

def getTransaction():
    """
    Creates a transaction required for database updates. Currently, nested
    transactions are not supported. Subsequent calls to C{getTransaction}
    without commiting the first transaction will return the same handle.
    
    @rtype: L{Transaction<porcupine.db.transaction.Transaction>}
    """
    txn = currentThread().trans
    if not txn or txn._iscommited:
        txn = currentThread().trans = _db.db_handle.transaction()
    return txn
