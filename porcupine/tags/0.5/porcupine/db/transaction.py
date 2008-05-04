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
"Porcupine Server Transaction classes"
import copy
import time

from porcupine.db import _db
from porcupine import exceptions

class Transaction(object):
    "The main type of a Porcupine transaction."
    def __init__(self):
        self.actions = []
        self.txn = _db.createTransaction()
        self._iscommited = False
        self._retries = 0

    def retry(self):
        """
        Called by the application server whenever a transaction commit fails.
        
        @return: None
        
        @raise porcupine.exceptions.DBTransactionIncomplete:
            if the maximum number of transaction retries has been reached,
            as defined in the C{porcupine.ini} file.
        """
        while self._retries < _db.db_handle.trans_max_retries:
            _db.abortTransaction(self.txn)
            self._retries += 1
            time.sleep(0.05)
            self.txn = _db.createTransaction()
            try:
                tmpActions, self.actions = copy.copy(self.actions), []
                dummy = [func(*args) for func,args in tmpActions]
                return
            except exceptions.DBTransactionIncomplete:
                pass
        else:
            raise exceptions.DBTransactionIncomplete

    def commit(self):
        """
        Commits the transaction.
        
        @return: None
        
        @raise porcupine.exceptions.DBTransactionIncomplete:
            if the maximum number of transaction retries has been reached,
            as defined in the C{porcupine.ini} file.
        """
        while self._retries < _db.db_handle.trans_max_retries:
            try:
#                if self._retries == 1:
#                    raise exceptions.DBTransactionIncomplete
                _db.commitTransaction(self.txn)
                self._iscommited = True
                return
            except exceptions.DBTransactionIncomplete:
                self.retry()
        else:
            raise exceptions.DBTransactionIncomplete

    def abort(self):
        """
        Aborts the transaction.
        
        @return: None
        """
        _db.abortTransaction(self.txn)
