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
Porcupine Server BDB Transaction class
"""
from bsddb import db

from porcupine import exceptions
from porcupine.db.basetransaction import BaseTransaction

class Transaction(BaseTransaction):
    def __init__(self, env):
        self.env = env
        self.txn = env.txn_begin()
        BaseTransaction.__init__(self)

    def _retry(self):
        self.txn = self.env.txn_begin()
        BaseTransaction._retry(self)

    def commit(self):
        """
        Commits the transaction.

        @return: None
        """
        try:
            self.txn.commit()
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete
        BaseTransaction.commit(self)

    def abort(self):
        """
        Aborts the transaction.

        @return: None
        """
        self.txn.abort()
        BaseTransaction.abort(self)
