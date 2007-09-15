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
"Porcupine Server Transaction classes"

import copy, time

from porcupine.db import db
from porcupine.core.management import Mgt
from porcupine import serverExceptions
from porcupine.core import management

class Transaction(object):
    "The main type of a Porcupine transaction."
    def __init__(self):
        self.actions = []
        self.txn = db.createTransaction()
        self._iscommited = False
        self._retries = 0

    def retry(self):
        """
        Called by the application server whenever a transaction commit fails.
        
        @return: None
        
        @raise porcupine.serverExceptions.DBTransactionIncomplete:
            if the maximum number of transaction retries has been reached,
            as defined in the C{porcupine.ini} file.
        """
        while self._retries < db.db_handle.trans_max_retries:
            db.abortTransaction(self.txn)
            self._retries += 1
            time.sleep(0.05)
            self.txn = db.createTransaction()
            try:
                tmpActions, self.actions = copy.copy(self.actions), []
                dummy = [func(*args) for func,args in tmpActions]
                return
            except serverExceptions.DBTransactionIncomplete:
                pass
        else:
            raise serverExceptions.DBTransactionIncomplete

    def commit(self):
        """
        Commits the transaction.
        
        @return: None
        
        @raise porcupine.serverExceptions.DBTransactionIncomplete:
            if the maximum number of transaction retries has been reached,
            as defined in the C{porcupine.ini} file.
        """
        while self._retries < db.db_handle.trans_max_retries:
            try:
#                if self._retries == 1:
#                    raise serverExceptions.DBTransactionIncomplete
                db.commitTransaction(self.txn)
                self._iscommited = True
                return
            except serverExceptions.DBTransactionIncomplete:
                self.retry()
        else:
            raise serverExceptions.DBTransactionIncomplete

    def abort(self):
        """
        Aborts the transaction.
        
        @return: None
        """
        db.abortTransaction(self.txn)

class XTransaction(Transaction):
    "Transaction class used on replicated environments."
    def __init__(self):
        Transaction.__init__(self)
        self.data = {0:{}, 1:{}}

    def commit(self):
        Transaction.commit(self)
        # broadcast transaction data
        Mgt.mgtServer.sendMessage(management.REP_BROADCAST, 'TRANS_DATA', (time.clock(), self.data))

    def repl_commit(self, data):
        retries = 0
        while retries < db.db_handle.trans_max_retries:
            try:
                for sId in data[1].keys():
                    if data[1][sId] != -1:
                        db.db_handle.repl_putExternalAttribute(sId, data[1][sId], self)
                    else:
                        db.db_handle.repl_deleteExternalAttribute(sId, self)

                for sId in data[0].keys():
                    if data[0][sId] != -1:
                        db.db_handle.repl_putItem(sId, data[0][sId], self)
                    else:
                        db.db_handle.repl_deleteItem(sId, self)
                    
                db.commitTransaction(self.txn)
                return
            except serverExceptions.DBTransactionIncomplete:
                db.abortTransaction(self.txn)
                self.txn = db.createTransaction()
                retries += 1
                time.sleep(0.05)
        raise serverExceptions.DBTransactionIncomplete
