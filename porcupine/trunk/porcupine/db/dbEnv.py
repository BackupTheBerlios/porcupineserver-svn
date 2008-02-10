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
"Porcupine Server DB Enviroment singleton"

from threading import currentThread

from porcupine.config.services import services
from porcupine.db import db
from porcupine import serverExceptions
from porcupine.security import objectAccess

def getItem(sPath, trans=None):
    """
    Fetches an object from the database. If the user has no read permissions
    on the object then C{None} is returned.
    
    @param sPath: The object's ID or the object's full path.
    @type sPath: str
    
    @param trans: A valid transaction handle.
    
    @rtype: L{GenericItem<porcupine.systemObjects.GenericItem>}
    
    @raise porcupine.serverExceptions.ObjectNotFound: if the item does
           not exist
    """
    if (trans):
        trans.actions.append( (getItem, (sPath, trans)) )
    
    try:
        oItem = db.getItem(sPath, trans)
    except serverExceptions.DBTransactionIncomplete:
        trans.retry()

    # check read permissions
    if objectAccess.getAccess(oItem, currentThread().context.session.user) != 0:
        return(oItem)
    else:
        return(None)

def getTransaction():
    """
    Creates a transaction required for database updates. Currently, nested
    transactions are not supported. Subsequent calls to C{getTransaction}
    without commiting the first transaction will return the same handle.
    
    @rtype: L{Transaction<porcupine.db.transaction.Transaction>}
    """
    # check if server runs in replicated environment
    # and if it is the master
    if db.db_handle.supports_replication and not(services['management'].isMaster()):
        raise serverExceptions.ProxyRequest
    
    txn = currentThread().trans
    if not txn or txn._iscommited:
        # create transaction
        txn = currentThread().trans = db.db_handle.transaction()
    
    return txn