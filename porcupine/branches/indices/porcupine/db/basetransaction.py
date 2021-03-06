#===============================================================================
#    Copyright 2005-2009, Tassos Koutsovassilis
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
Porcupine Server Base Transaction class
"""
from porcupine.db import _db
from porcupine.config.settings import settings

class BaseTransaction(object):
    "The base type of a Porcupine transaction."
    txn_max_retries = 12
    if settings['store'].has_key('trans_max_retries'):
        txn_max_retries = int(settings['store']['trans_max_retries'])
    
    def __init__(self):
        self._iscommited = False
        _db._activeTxns += 1

    def _retry(self):
        _db._activeTxns += 1

    def commit(self):
        """
        Commits the transaction.

        @return: None
        """
        self._iscommited = True
        _db._activeTxns -= 1

    def abort(self):
        """
        Aborts the transaction.

        @return: None
        """
        _db._activeTxns -= 1
