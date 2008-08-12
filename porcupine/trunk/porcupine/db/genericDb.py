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
"Generic DB interface class"
from porcupine.db.transaction import Transaction

class GenericDBInterface(object):
    transaction = Transaction
    supports_backup = True
    
    # to be implemented by subclass
    def _truncate(self):
        raise NotImplementedError

    def _getItem(self, sOID, trans=None):
        raise NotImplementedError

    def _putItem(self, sOID, sItem, trans):
        raise NotImplementedError

    def _deleteItem(self, sID, trans):
        raise NotImplementedError

    def _getExternalAttribute(self, sID, trans):
        raise NotImplementedError

    def _putExternalAttribute(self, sID, sStream, trans):
        raise NotImplementedError

    def _deleteExternalAttribute(self, sID, trans):
        raise NotImplementedError

    def _getTransactionHandle(self):
        raise NotImplementedError

    def _abortTransaction(self, trans):
        raise NotImplementedError

    def _commitTransaction(self, trans):
        raise NotImplementedError
        
    def _backup(self, output_file):
        raise NotImplementedError
        
    def _restore(self, backup_file):
        raise NotImplementedError
    
    def _shrink(self):
        raise NotImplementedError

    def _recover(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
