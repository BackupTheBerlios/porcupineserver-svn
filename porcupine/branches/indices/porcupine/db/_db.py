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
"Porcupine Server DB Interface"
import time
import cPickle

from porcupine import exceptions
from porcupine.utils import misc
from porcupine.config.settings import settings

Transaction = None
_db_handle = None
_locks = 0
_activeTxns = 0

def open(**kwargs):
    global _db_handle, Transaction
    _db_handle = misc.getCallableByName(settings['store']['interface'])
    Transaction = _db_handle.Transaction
    _db_handle.open(**kwargs)
    
def is_open():
    return _db_handle.is_open()
    
def _getItemByPath(lstPath, trans=None):
    oItem = getItem('')
    for name in lstPath[1:len(lstPath)]:
        if name:
            child_id = oItem.getChildId(name)
            if child_id:
                oItem = getItem(child_id)
            else:
                return None
    return(_db_handle.getItem(child_id, trans))

def getItem(oid, trans=None):
    item = _db_handle.getItem(oid, trans)
    if item == None:
        lstPath = oid.split('/')
        iPathDepth = len(lstPath)
        if iPathDepth > 1:
            # /[itemID]
            if iPathDepth == 2:
                item = _db_handle.getItem(lstPath[1], trans)
            # /folder1/folder2/item
            if not item:
                item = _getItemByPath(lstPath, trans)
    if item != None:
        item = cPickle.loads(item)
        return item

def putItem(item, trans=None):
    _db_handle.putItem(item, trans)
    
def deleteItem(item, trans):
    _db_handle.deleteItem(item._id, trans)

def getExternal(id, trans):
    return _db_handle.getExternal(id, trans)

def putExternal(id, stream, trans):
    _db_handle.putExternal(id, stream, trans)
    
def deleteExternal(id, trans):
    _db_handle.deleteExternal(id, trans)

def handle_update(item, old_item, trans):
    if item._eventHandlers:
        if old_item:
            # update
            [handler.on_update(item, old_item, trans)
             for handler in item._eventHandlers]
        else:
            # create
            [handler.on_create(item, trans)
             for handler in item._eventHandlers]
    for attr_name in item.__props__:
        try:
            attr = getattr(item, attr_name)
        except AttributeError:
            continue
        attr.validate()
        if attr._eventHandler:
            if old_item:
                # it is an update
                old_attr = getattr(old_item, attr_name)
                attr._eventHandler.on_update(item, attr, old_attr, trans)
            else:
                # it is a new object
                attr._eventHandler.on_create(item, attr, trans)

def handle_delete(item, trans, is_permanent):
    if item._eventHandlers:
        [handler.on_delete(item, trans, is_permanent) 
         for handler in item._eventHandlers]
    attrs = [getattr(item, attr_name)
             for attr_name in item.__props__
             if hasattr(item, attr_name)]
    [attr._eventHandler.on_delete(item, attr, trans, is_permanent)
     for attr in attrs
     if attr._eventHandler]

def handle_undelete(item, trans):
    attrs = [getattr(item, attr_name)
             for attr_name in item.__props__
             if hasattr(item, attr_name)]
    [attr._eventHandler.on_undelete(item, attr, trans)
     for attr in attrs
     if attr._eventHandler]
    
# indices
def query_index(index, value, trans, fetch_all=False, resolve_shortcuts=False):
    return _db_handle.query_index(index, value, trans,
                                  fetch_all, resolve_shortcuts)

def natural_join(conditions, trans, fetch_all=False, resolve_shortcuts=False):
    return _db_handle.natural_join(conditions, trans,
                                   fetch_all, resolve_shortcuts)

def test_natural_join(conditions, trans):
    return _db_handle.test_natural_join(conditions, trans)

# transactions
def createTransaction():
    global _activeTxns
    while _locks:
        time.sleep(1)
    txn = _db_handle.getTransaction()
    _activeTxns += 1
    return(txn)
   
def abortTransaction(txn):
    global _activeTxns
    _db_handle.abortTransaction(txn)
    _activeTxns -= 1

def commitTransaction(txn):
    global _activeTxns
    _db_handle.commitTransaction(txn)
    _activeTxns -= 1

# administrative
def lock():
    global _locks
    _locks += 1
    # allow active transactions to commit or abort...
    while _activeTxns:
        time.sleep(0.5)

def unlock():
    global _locks
    if _locks:
        _locks -= 1

def recover():
    _db_handle.recover()
    
def backup(output_file):
    _db_handle.backup(output_file)
    
def restore(bset):
    _db_handle.restore(bset)

def truncate():
    _db_handle.truncate()

def shrink():
    _db_handle.shrink()

def close():
    _db_handle.close()
