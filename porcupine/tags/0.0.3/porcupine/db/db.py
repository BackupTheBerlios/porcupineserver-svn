#===============================================================================
#    Copyright 2005, Tassos Koutsovassilis
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

import time, cPickle

from porcupine import serverExceptions

_locks = 0
_activeTxns = 0
db_handle = None
    
def open(db_handleClass):
    global db_handle
    db_handle = db_handleClass()
        
def __getItemByPath(lstPath, trans=None):
    oItem = getItem('')
    for sName in lstPath[1:len(lstPath)]:
        if sName:
            childId = oItem.getChildId(sName)
            if childId:
                oItem = getItem(childId)
            else:
                return None
    return(db_handle._getItem(childId, trans))

def getItem(sOID, trans=None):
    # [itemID]
    sItem = db_handle._getItem(sOID, trans)
    if not sItem:
        lstPath = sOID.split('/')
        iPathDepth = len(lstPath)
        if iPathDepth > 1:
            # /[itemID]
            if len(lstPath)==2:
                sItem = db_handle._getItem(lstPath[1], trans)
            # /folder1/folder2/item
            if not sItem:
                sItem = __getItemByPath(lstPath, trans)

    if sItem:
        oItem = cPickle.loads(sItem)
        if oItem._isDeleted:
            raise serverExceptions.DBItemNotFound, 'The object "%s" does not exist' % sOID
        return oItem
    else:
        raise serverExceptions.DBItemNotFound, 'The object "%s" does not exist' % sOID

def putItem(oItem, trans=None):
    db_handle._putItem(oItem._id, cPickle.dumps(oItem, 2), trans)

def deleteItem(oItem, trans):
    db_handle._deleteItem(oItem._id, trans)

def getDeletedItem(sOID, trans=None):
    sItem = db_handle._getItem(sOID, trans)
    if not(sItem):
        raise serverExceptions.DBItemNotFound, 'The deleted object "%s" no longer exists' % sOID
    else:
        oItem = cPickle.loads(sItem)
        return(oItem)
        
def removeDeletedItem(oItem, trans):
    handle_delete(oItem, trans, True)
    db_handle._deleteItem(oItem._id, trans)
    
    if oItem.isCollection:
        lstChildren = oItem._items.values() + oItem._subfolders.values()
        for sID in lstChildren:
            oChild = getDeletedItem(sID, trans)
            removeDeletedItem(oChild, trans)

def handle_update(oItem, oOldItem, trans):
    attrs = [
        getattr(oItem, attr_name)
        for attr_name in oItem.__props__
        if hasattr(oItem, attr_name)
    ]
    for oAttr in attrs:
        oAttr.validate()
        if oAttr._eventHandler:
            if oOldItem:
                # it is an update
                old_attr = getattr(oOldItem, oAttr.__class__.__name__)
                oAttr._eventHandler.on_update(oItem, oAttr, old_attr, trans)
            else:
                # it is a new object or undeleting
                oAttr._eventHandler.on_create(oItem, oAttr, trans)

def handle_delete(oItem, trans, bPermanent):
    attrs = [
        getattr(oItem, attr_name)
        for attr_name in oItem.__props__
        if hasattr(oItem, attr_name)
    ]
    dummy_list = [
        attr._eventHandler.on_delete(oItem, attr, trans, bPermanent)
        for attr in attrs
        if attr._eventHandler
    ]

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

def createTransaction():
    global _activeTxns
    while _locks:
        time.sleep(1)
    txn = db_handle._getTransactionHandle()
    _activeTxns += 1
    return(txn)
   
def abortTransaction(txn):
    global _activeTxns
    _activeTxns -= 1
    db_handle._abortTransaction(txn)

def commitTransaction(txn):
    global _activeTxns
    _activeTxns -= 1
    db_handle._commitTransaction(txn)

def close():
    db_handle.close()
