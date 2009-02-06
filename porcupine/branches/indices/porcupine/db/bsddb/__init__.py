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
Porcupine server Berkeley DB interface
"""
import os
import time
import logging
import cPickle
import glob
from bsddb import db
from threading import Thread

from porcupine import exceptions
from porcupine.config.settings import settings
from porcupine.core.objectSet import ObjectSet
from porcupine.utils.db.backup import BackupFile
from porcupine.db.bsddb.transaction import Transaction
from porcupine.db.bsddb.index import DbIndex
from porcupine.db.bsddb.cursor import Cursor, Join

_running = False
_env = None
_itemdb = None
_docdb = None
_indices = {}
_maintenance_thread = None
_dir = None
_checkpoint_interval = 1

logger = logging.getLogger('serverlog')

def open(**kwargs):
    global _env, _itemdb, _docdb, _running, _maintenance_thread, _dir
    
    _dir = settings['store']['bdb_data_dir']
    # add trailing '/'
    if _dir[-1] != '/':
        _dir += '/'
    
    if settings['store'].has_key('checkpoint_interval'):
        global _checkpoint_interval
        _checkpoint_interval = int(settings['store']['checkpoint_interval'])
    
    # create db environment
    additional_flags = kwargs.get('flags', 0)
    _env = db.DBEnv()
    _env.set_timeout(int(settings['store']['lock_timeout']),
                     db.DB_SET_LOCK_TIMEOUT)
    _env.set_timeout(int(settings['store']['txn_timeout']),
                     db.DB_SET_TXN_TIMEOUT)
    _env.open(
        _dir,
        db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
        db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_CREATE | 
        additional_flags
    )
    
    dbMode = 0660
    dbFlags = db.DB_THREAD | db.DB_CREATE | db.DB_AUTO_COMMIT
    
    # open items db
    _itemdb = db.DB(_env)
    _itemdb.open(
        'porcupine.db',
        'items',
        dbtype = db.DB_HASH,
        mode = dbMode,
        flags = dbFlags
    )
    
    # open documents db
    _docdb = db.DB(_env)
    _docdb.open(
        'porcupine.db',
        'docs',
        dbtype = db.DB_HASH,
        mode = dbMode,
        flags = dbFlags
    )
    
    # open indices
    for name, unique in settings['store']['indices']:
        _indices[name] = DbIndex(_env, _itemdb, name, unique)
    
    _running = True
    _maintenance_thread = Thread(target=__maintain,
                                 name='Berkeley DB maintenance thread')
    _maintenance_thread.start()
    
def is_open():
    return _running

# item operations
def getItem(oid, trans=None):
    try:
        return _itemdb.get(oid, txn=trans and trans.txn, flags=db.DB_RMW)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

def putItem(item, trans=None):
    try:
        _itemdb.put(item._id, cPickle.dumps(item, 2), trans and trans.txn)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

def deleteItem(oid, trans):
    try:
        _itemdb.delete(oid, trans and trans.txn)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

# external attributes
def getExternal(id, trans):
    try:
        return _docdb.get(id, txn=trans and trans.txn)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

def putExternal(id, stream, trans):
    try:
        _docdb.put(id, stream, trans and trans.txn)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

def deleteExternal(id, trans):
    try:
        _docdb.delete(id, trans and trans.txn)
    except (db.DBLockDeadlockError, db.DBLockNotGrantedError):
        raise exceptions.DBTransactionIncomplete

# indices
def query_index(index, value, trans, fetch_all, resolve_shortcuts):
    cursor = Cursor(_indices[index], trans and trans.txn, fetch_all=fetch_all,
                    resolve_shortcuts=resolve_shortcuts)
    cursor.set(value)
    results = ObjectSet([x for x in cursor])
    cursor.close()
    return(results)

def natural_join(conditions, trans, fetch_all, resolve_shortcuts):
    cur_list = []
    for index, value in conditions:
        cursor = Cursor(_indices[index], trans and trans.txn)
        cursor.set(value)
        cur_list.append(cursor)
    c_join = Join(_itemdb, cur_list, trans, fetch_all=fetch_all,
                  resolve_shortcuts=resolve_shortcuts)
    results = ObjectSet([x for x in c_join])
    c_join.close()
    [cur.close() for cur in cur_list]
    return results

def test_natural_join(conditions, trans):
    cur_list = []
    for index, value in conditions:
        cursor = Cursor(_indices[index], trans and trans.txn)
        cursor.set(value)
        cur_list.append(cursor)
    c_join = Join(_itemdb, cur_list, trans)
    result = bool(c_join.next())
    c_join.close()
    [cur.close() for cur in cur_list]
    return result

# transactions
def get_transaction():
    return Transaction(_env)

# administrative
def __removeFiles():
    oldFiles = glob.glob(_dir + '__db.*')
    for oldFile in oldFiles:
        os.remove(oldFile)
    # log files
    oldFiles = glob.glob(_dir + 'log.*')
    for oldFile in oldFiles:
        os.remove(oldFile)
    # database file
    os.remove(_dir + 'porcupine.db')
    # index file
    os.remove(_dir + 'porcupine.idx')
        
def truncate():
    # older versions of bsddb do not support truncate
    if hasattr(_itemdb, 'truncate'):
        _itemdb.truncate()
        _docdb.truncate()
    else:
        # close database
        close()
        # remove old database files
        __removeFiles()
        # open db
        open()
    
def recover():
    open(flags=db.DB_RECOVER)

def backup(output_file):
    if not os.path.isdir(os.path.dirname(output_file)):
        raise IOError
    # force checkpoint
    _env.txn_checkpoint(0, 0, db.DB_FORCE)
    logs = _env.log_archive(db.DB_ARCH_LOG)
    logs.sort()
    backfiles = (_dir + 'porcupine.db', _dir + logs[-1])
    # compact backup....
    backupFile = BackupFile(output_file)
    backupFile.addfiles(backfiles)
        
def restore(bset):
    if not os.path.exists(bset):
        raise IOError
    close()
    __removeFiles()
    backupFile = BackupFile(bset)
    backupFile.extractTo(_dir)
    open()

def shrink():
    logs = _env.log_archive()
    for log in logs:
        os.remove(_dir + log)
    return len(logs)

def __maintain():
    from porcupine.db import _db
    while _running:
        time.sleep(0.5)
        # deadlock detection
        try:
            aborted = _env.lock_detect(db.DB_LOCK_RANDOM, db.DB_LOCK_CONFLICT)
            if aborted:
                _db._activeTxns -= aborted
                logger.critical("Deadlock: Aborted %d deadlocked transaction(s)" % aborted)
        except db.DBError:
            pass
        # checkpoint
        _env.txn_checkpoint(0, _checkpoint_interval, 0)

def close():
    global _running
    _running = False
    if _maintenance_thread != None:
        _maintenance_thread.join()
    _itemdb.close()
    _docdb.close()
    for index in _indices:
        _indices[index].close()
    _env.close()
