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
"Berkeley DB interfaces"

import time, logging, os, os.path
from bsddb import db
from threading import Thread

from porcupine.db.genericDb import GenericDBInterface, DBReplicator
from porcupine.utils import backup
from porcupine import serverExceptions

logger = logging.getLogger('serverlog')

class DbInterface(GenericDBInterface):
    """
    Porcupine server Berkeley DB interface
    """
    def __init__(self):
        GenericDBInterface.__init__(self)
        
        from porcupine.config import dbparams
        
        try:
            self.dir = dbparams.params['bdb_data_dir']
        except KeyError:
            raise serverExceptions.ConfigurationError, (('bdb_data_dir', \
                    'storeparameters'),)
        
        # add trailing '/'
        if self.dir[-1] != '/':
            self.dir += '/'

        try:
            self.trans_max_retries = int(dbparams.params['trans_max_retries'])
        except KeyError:
            # trans max retries default setting is 12
            trans_max_retries = 12
        except ValueError:
            raise serverExceptions.ConfigurationError, \
                'Invalid trans_max_retries setting: %s' % \
                dbparams.params[trans_max_retries]

        try:
            self.checkpoint_interval = int(dbparams.params['checkpoint_interval'])
        except KeyError:
            # default checkpoint interval set to 1 minute
            self.checkpoint_interval = 1
        except ValueError:
            raise serverExceptions.ConfigurationError, \
                'Invalid checkpoint_interval setting: %s' % \
                dbparams.params[checkpoint_interval]

        # create db environment
        self._env = db.DBEnv()
        self._env.open(
            self.dir,
            db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
            db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_CREATE  | db.DB_RECOVER
        )

        self._env.set_flags(db.DB_AUTO_COMMIT, 1)

        dbMode = 0660
        # open items db
        self._itemdb = db.DB(self._env)
        self._itemdb.open(
            'porcupine.db',
            'items',
            dbtype=db.DB_HASH,
            mode=dbMode,
            flags=db.DB_THREAD | db.DB_CREATE
        )
        # open documents db
        self._docdb = db.DB(self._env)
        self._docdb.open(
            'porcupine.db',
            'docs',
            dbtype=db.DB_HASH,
            mode=dbMode,
            flags=db.DB_THREAD | db.DB_CREATE
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

    def _getItem(self, sOID, trans=None):
        try:
            return self._itemdb.get(sOID, txn=trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _putItem(self, sOID, sItem, trans):
        try:
            self._itemdb.put(sOID, sItem, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _deleteItem(self, sID, trans):
        try:
            self._itemdb.delete(sID, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _getExternalAttribute(self, sID, trans=None):
        try:
            return(self._docdb.get(sID, txn=trans and trans.txn))
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _putExternalAttribute(self, sID, sStream, trans):
        try:
            self._docdb.put(sID, sStream, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _deleteExternalAttribute(self, sID, trans):
        try:
            self._docdb.delete(sID, trans and trans.txn)
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

    def _getTransactionHandle(self):
        return(self._env.txn_begin())

    def _abortTransaction(self, txn):
        txn.abort()

    def _commitTransaction(self, txn):
        try:
            txn.commit()
        except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
            raise serverExceptions.DBTransactionIncomplete

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
                    from porcupine.db import db as dbhandle
                    dbhandle._activeTxns -= aborted
                    logger.critical("Deadlock: Aborted %d deadlocked transaction(s)" % aborted)
            except db.DBError:
                pass

    def close(self):
        self.running = False
        self.mt.join()
        self._itemdb.close()
        self._docdb.close()
        self._env.close()

class XDbInterface(DBReplicator, DbInterface):
    """
    Porcupine server Berkeley DB interface
    for replicated environments
    """
    def __init__(self):
        DbInterface.__init__(self)
        # do not use durable transactions
        # let the checkpointing do the job...
        self._env.set_flags(db.DB_TXN_NOSYNC, 1)
        DBReplicator.__init__(self)

    def enumerate(self):
        # get objects
        cursor = self._itemdb.cursor()
        rec = cursor.first()
        while rec is not None:
            yield [0, rec]
            rec = cursor.next()
        cursor.close()
        # get files
        cursor = self._docdb.cursor()
        rec = cursor.first()
        while rec is not None:
            yield [1, rec]
            rec = cursor.next()
        cursor.close()
