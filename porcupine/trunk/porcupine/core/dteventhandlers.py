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
"Porcupine server built-in datatypes event handlers"
import os

from porcupine import db
from porcupine.db import _db
from porcupine import exceptions
from porcupine.utils import misc

class DatatypeEventHandler(object):
    @staticmethod
    def on_create(item, attr, trans):
        pass

    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        pass
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        pass

class CompositionEventHandler(DatatypeEventHandler):
    "Composition datatype event handler"
    
    @staticmethod
    def on_create(item, attr, trans):
        if item._isDeleted:
            attr.value = [_db.getDeletedItem(sID, trans)
                          for sID in attr.value]
        CompositionEventHandler.on_update(item, attr, None, trans)
        
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        from porcupine.systemObjects import Composite
        # load objects
        dctObjects = {}
        for i, obj in enumerate(new_attr.value):
            if isinstance(obj, Composite):
                obj._containerid = item._id
            elif isinstance(obj, str):
                obj = _db.getItem(obj, trans)
                new_attr.value[i] = obj
            else:
                raise exceptions.ContainmentError, \
                    'Invalid object type "%s" in composition.' % \
                    obj.__class__.__name__
            dctObjects[obj._id] = obj
        
        # check containment
        compositeClass = misc.getCallableByName(new_attr.compositeClass)
        
        if [obj for obj in dctObjects.values()
                if not isinstance(obj, compositeClass)]:
            raise exceptions.ContainmentError, \
                'Invalid content class "%s" in composition.' % \
                obj.getContentclass()
        
        # get previous value
        if old_attr != None:
            old_ids = set(old_attr.value)
        else:
            old_ids = set()
        
        new_ids = set([obj._id for obj in new_attr.value])
        
        # calculate added composites
        lstAdded = list(new_ids - old_ids)
        for obj_id in lstAdded:
            _db.handle_update(dctObjects[obj_id], None, trans)
            dctObjects[obj_id]._isDeleted = False
            _db.putItem(dctObjects[obj_id], trans)
        
        # calculate constant composites
        lstConstant = list(new_ids & old_ids)
        for obj_id in lstConstant:
            _db.handle_update(dctObjects[obj_id],
                                 _db.getItem(obj_id, trans),
                                 trans)
            _db.putItem(dctObjects[obj_id], trans)
        
        # calculate removed composites
        lstRemoved = list(old_ids - new_ids)
        for obj_id in lstRemoved:
            composite4removal = _db.getItem(obj_id, trans)
            CompositionEventHandler.removeComposite(composite4removal, trans)
        
        new_attr.value = list(new_ids)
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if bPermanent:
            if item._isDeleted:
                func_get = _db.getDeletedItem
            else:
                func_get = _db.getItem
            composites = [func_get(sID, trans) for sID in attr.value]
            for composite in composites:
                CompositionEventHandler.removeComposite(composite, trans)
        else:
            for sID in attr.value:
                composite = _db.getItem(sID, trans)
                _db.handle_delete(composite, trans, False)
                composite._isDeleted = True
                _db.putItem(composite, trans)
    
    @staticmethod
    def removeComposite(composite, trans):
        _db.handle_delete(composite, trans, True)
        _db.deleteItem(composite, trans)
        
class RelatorNEventHandler(DatatypeEventHandler):
    "RelatorN datatype event handler"
    
    @staticmethod
    def on_create(item, attr, trans):
        RelatorNEventHandler.on_update(item, attr, None, trans)
    
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        from porcupine import datatypes
        # remove duplicates
        new_attr.value = list(set(new_attr.value))
        
        # get previous value
        if old_attr:
            prvValue = set(old_attr.value)
            noAccessList = RelatorNEventHandler.getNoAccessIds(old_attr, trans)
        else:
            prvValue = set()
            noAccessList = []

        # get current value
        currentValue = set(new_attr.value + noAccessList)

        if currentValue != prvValue:
            # calculate added references
            lstAdded = list(currentValue - prvValue)
            for sID in lstAdded:
                oItemRef = _db.getItem(sID, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    _db.putItem(oItemRef, trans)
                else:
                    new_attr.value.remove(sID)
    
            # calculate removed references
            lstRemoved = list(prvValue - currentValue)
            for sID in lstRemoved:
                oItemRef = _db.getItem(sID, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                _db.putItem(oItemRef, trans)
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes

            lstValue = attr.value
            if lstValue and attr.respectsReferences:
                raise exceptions.ReferentialIntegrityError, (
                    'Cannot delete object "%s" ' % item.displayName.value +
                    'because it is being referenced by other objects.')
            
            # remove references
            for sID in lstValue:
                oItemRef = _db.getItem(sID, trans)
                if oItemRef.getContentclass() in attr.relCc:
                    oAttrRef = getattr(oItemRef, attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        try:
                            oAttrRef.value.remove(item._id)
                        except ValueError:
                            pass
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = ''
                    _db.putItem(oItemRef, trans)
                else:
                    attr.value.remove(sID)
    
    @staticmethod
    def getNoAccessIds(attr, trans):
        lstNoAccess = []
        for sID in attr.value:
            oItem = db.getItem(sID, trans)
            # do not replay in case of txn abort
            # del trans.actions[-1]
            if not(oItem):
                lstNoAccess.append(sID)
        return lstNoAccess
    
class Relator1EventHandler(DatatypeEventHandler):
    "Relator1 datatype event handler"

    @staticmethod
    def on_create(item, attr, trans):
        Relator1EventHandler.on_update(item, attr, None, trans)
 
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        from porcupine import datatypes
        
        # get previous value
        if old_attr:
            prvValue = old_attr.value
        else:
            prvValue = ''
        
        if new_attr.value != prvValue:
            if new_attr.value:
                oItemRef = _db.getItem(new_attr.value, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    _db.putItem(oItemRef, trans)
                else:
                    new_attr.value = ''
            if prvValue:
                oItemRef = _db.getItem(prvValue, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                _db.putItem(oItemRef, trans)

    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes
            if attr.value:
                if attr.respectsReferences:
                    raise exceptions.ReferentialIntegrityError, (
                        'Cannot delete object "%s" ' % item.displayName.value +
                        'because it is referenced by other objects.')
                # remove reference
                oItemRef = _db.getItem(attr.value, trans)
                oAttrRef = getattr(oItemRef, attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                _db.putItem(oItemRef, trans)

class ExternalAttributeEventHandler(DatatypeEventHandler):
    "External attribute event handler"

    @staticmethod
    def on_create(item, attr, trans):
        ExternalAttributeEventHandler.on_update(item, attr, None, trans)
    
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        if new_attr.isDirty:
            _db.db_handle._putExternalAttribute(new_attr._id, new_attr.value, trans)
        new_attr._reset()
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if bPermanent:
            _db.db_handle._deleteExternalAttribute(attr._id, trans)

class ExternalFileEventHandler(DatatypeEventHandler):
    "External file event handler"
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if bPermanent and attr.removeFileOnDeletion:
            try:
                os.remove(attr.value)
            except OSError:
                pass
