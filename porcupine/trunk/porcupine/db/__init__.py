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
import time
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
    oItem = _db.getItem(sPath, trans)
    # check read permissions
    if objectAccess.getAccess(oItem, currentThread().context.session.user) != 0:
        return oItem
    else:
        return None

def getTransaction():
    """
    Returns a transaction handle required for database updates.
    Currently, nested transactions are not supported.
    Subsequent calls to C{getTransaction} will return the same handle.
    
    @rtype: L{Transaction<porcupine.db.transaction.Transaction>}
    """
    txn = currentThread().trans
    if txn == None:
        raise exceptions.InternalServerError, \
            "The specified method is not defined as transactional."
    return txn

def transactional(auto_commit=False):
    def transactional_decorator(function):
        """
        This is the descriptor for making a method of a content class
        transactional.
        """
        def transactional_wrapper(*args, **kwargs):
            c_thread = currentThread()
            if c_thread.trans == None:
                txn = _db.db_handle.transaction()
                c_thread.trans = txn
            else:
                txn = c_thread.trans
            retries = 0
            try:
                while retries < _db.db_handle.trans_max_retries:
                    try:
                        #if retries == 0:
                        #    raise exceptions.DBTransactionIncomplete
                        val = function(*args)
                        if auto_commit:
                            ac = kwargs.get('commit', auto_commit)
                            if ac:
                                txn.commit()
                        return val
                    except exceptions.DBTransactionIncomplete:
                        txn.abort()
                        time.sleep(0.05)
                        retries += 1
                        txn._retry()
                else:
                    raise exceptions.DBTransactionIncomplete
            finally:
                # abort uncommitted transactions
                if not txn._iscommited:
                    txn.abort()
                c_thread.trans = None
        transactional_wrapper.func_name = function.func_name
        transactional_wrapper.func_doc = function.func_doc
        return transactional_wrapper
    return transactional_decorator
