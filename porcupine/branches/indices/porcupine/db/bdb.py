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
"Berkeley DB interfaces"

import os
import time
import logging
from bsddb import db
from threading import Thread

from porcupine.db import _db
from porcupine.config.settings import settings
from porcupine.db.genericDb import GenericDBInterface
from porcupine.utils.db import backup
from porcupine import exceptions

logger = logging.getLogger('serverlog')

class DbInterface(GenericDBInterface):
    """
    Porcupine server Berkeley DB interface
    """
    def __init__(self, **kwargs):
        GenericDBInterface.__init__(self)
        
        self.dir = settings['store']['bdb_data_dir']
        
        # add trailing '/'
        if self.dir[-1] != '/':
            self.dir += '/'

        try:
            self.trans_max_retries = int(settings['store']['trans_max_retries'])
        except KeyError:
            # trans max retries default setting is 12
            self.trans_max_retries = 12

        try:
            self.checkpoint_interval = int(settings['store']['checkpoint_interval'])
        except KeyError:
            # default checkpoint interval set to 1 minute
            self.checkpoint_interval = 1

        additional_flags = kwargs.get('flags', 0)

        # create db environment
        self._env = db.DBEnv()
        self._env.open(
            self.dir,
            db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
            db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_CREATE | additional_flags
        )
        
        dbMode = 0660
        dbFlags = db.DB_THREAD | db.DB_CREATE | db.DB_AUTO_COMMIT
        # open items db
        self._itemdb = db.DB(self._env)
        self._itemdb.open(
            'porcupine.db',
            'items',
            dbtype=db.DB_HASH,
            mode=dbMode,
            flags=dbFlags
        )
        # open documents db
        self._docdb = db.DB(self._env)
        self._docdb.open(
            'porcupine.db',
            'docs',
            dbtype=db.DB_HASH,
            mode=dbMode,
            flags=dbFlags
        )
        # open indices
        self._tree = db.DB(self._env)
        self._tree.open(
            'porcupine.idx',
            '__tree',
            dbtype=db.DB_BTREE,
            mode=dbMode,
            flags=dbFlags
        )
        
        self._indices = {}
        for index in _db._indices:
            self._indices[index] = db.DB(self._env)
            self._indices[index].open(
                'porcupine.idx',
                index,
                dbtype=db.DB_BTREE,
                mode=dbMode,
                flags=dbFlags
            )
        
        self.running = True
        self.mt = Thread(target=self.maintain, \
                         name='Berkeley DB maintenance thread')
        self.mt.start()
        
    def __removeFiles(self):
        import glob
        oldFiles = glob.glob(self.dir + '__db.*')
        for oldFile in oldFiles:
            os.remove(oldFile)
        # log files
        oldFiles = glob.glob(self.dir + 'log.*')
        for oldFile in oldFiles:
            os.remove(oldFile)
        # database file
        os.remove(self.dir + 'porcupine.db')
        # index file
        os.remove(self.dir + 'porcupine.idx')

    def _truncate(self):
        # older versions of bsddb do not support truncate!
        if hasattr(self._itemdb, 'truncate'):
            self._itemdb.truncate()
            self._docdb.truncate()
        else:
            # close database
            self.close()
            # remove old database files
            self.__removeFiles()
            # reinitialize db
            self.__init__()
    
    @classmethod        
    def _recover(cls):
        return cls(flags=db.DB_RECOVER)

    def _getItem(self, sOID, trans=None):
        try:
            return self._itemdb.get(sOID, txn=trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _putItem(self, sOID, sItem, trans):
        try:
            self._itemdb.put(sOID, sItem, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _deleteItem(self, sID, trans):
        try:
            self._itemdb.delete(sID, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _getExternalAttribute(self, sID, trans=None):
        try:
            return(self._docdb.get(sID, txn=trans and trans.txn))
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _putExternalAttribute(self, sID, sStream, trans):
        try:
            self._docdb.put(sID, sStream, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _deleteExternalAttribute(self, sID, trans):
        try:
            self._docdb.delete(sID, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _getTransactionHandle(self):
        return(self._env.txn_begin())

    def _abortTransaction(self, txn):
        txn.abort()

    def _commitTransaction(self, txn):
        try:
            txn.commit()
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise exceptions.DBTransactionIncomplete

    def _backup(self, output_file):
        if not os.path.isdir(os.path.dirname(output_file)):
            raise IOError
        # force checkpoint
        self._env.txn_checkpoint(0, 0, db.DB_FORCE)
        logs = self._env.log_archive(db.DB_ARCH_LOG)
        logs.sort()
        backfiles = (self.dir + 'porcupine.db', self.dir + logs[-1])
        # compact backup....
        backupFile = backup.BackupFile(output_file)
        backupFile.addfiles(backfiles)
        
    def _restore(self, bset):
        if not os.path.exists(bset):
            raise IOError
        self.close()
        # delete files....
        self.__removeFiles()
        backupFile = backup.BackupFile(bset)
        backupFile.extractTo(self.dir)
        self.__init__()

    def _shrink(self):
        logs = self._env.log_archive()
        for log in logs:
            os.remove(self.dir + log)
        return len(logs)

    def maintain(self):
        while self.running:
            time.sleep(1.0)
            # checkpoint
            self._env.txn_checkpoint(0, self.checkpoint_interval, 0)
            # deadlock detection
            try:
                aborted = self._env.lock_detect(db.DB_LOCK_RANDOM, db.DB_LOCK_CONFLICT)
                if aborted:
                    _db._activeTxns -= aborted
                    logger.critical("Deadlock: Aborted %d deadlocked transaction(s)" % aborted)
            except db.DBError:
                pass

    def close(self):
        self.running = False
        self.mt.join()
        self._itemdb.close()
        self._docdb.close()
        self._tree.close()
        for index in self._indices:
            self._indices[index].close()
        self._env.close()
