#===============================================================================
#    Copyright 2005, 2006 Tassos Koutsovassilis
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

from porcupine import serverExceptions
from porcupine.core import eventHandlers
from porcupine.db import db, dbEnv

class CompositionEventHandler(eventHandlers.DatatypeEventHandler):
    "Composition datatype event handler"
    
    @staticmethod
    def on_create(item, attr, trans):
        if item._isDeleted:
            attr.value = [db.getDeletedItem(sID, trans) for sID in attr.value]
        CompositionEventHandler.on_update(item, attr, None, trans)
        
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        # check containment
        if [obj for obj in new_attr.value
            if obj.getContentclass() != new_attr.compositeClass]:
            raise serverExceptions.ContainmentError
        
        dctObjects = {}
        for obj in new_attr.value:
            obj._containerid = item._id
            dctObjects[obj._id] = obj
            
        new_ids = set([obj._id for obj in new_attr.value])
        
        # get previous value
        if old_attr:
            old_ids = set(old_attr.value)
        else:
            old_ids = set()

        # calculate added composites
        lstAdded = list(new_ids - old_ids)
        for sID in lstAdded:
            db.handle_update(dctObjects[sID], None, trans)
            dctObjects[sID]._isDeleted = False
            db.putItem(dctObjects[sID], trans)
            
        # calculate constant composites
        lstConstant = list(new_ids & old_ids)
        for sID in lstConstant:
            db.handle_update(dctObjects[sID], db.getItem(sID, trans) , trans)
            db.putItem(dctObjects[sID], trans)

        # calculate removed composites
        lstRemoved = list(old_ids - new_ids)
        for sID in lstRemoved:
            composite4removal = db.getItem(sID, trans)
            CompositionEventHandler.removeComposite(composite4removal, trans)
            
        new_attr.value = list(new_ids)
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if bPermanent:
            if item._isDeleted:
                func_get = db.getDeletedItem
            else:
                func_get = db.getItem
            composites = [func_get(sID, trans) for sID in attr.value]
            for composite in composites:
                CompositionEventHandler.removeComposite(composite, trans)
        else:
            for sID in attr.value:
                composite = db.getItem(sID, trans)
                db.handle_delete(composite, trans, False)
                composite._isDeleted = True
                db.putItem(composite, trans)
    
    @staticmethod
    def removeComposite(composite, trans):
        db.handle_delete(composite, trans, True)
        db.deleteItem(composite, trans)
        
class RelatorNEventHandler(eventHandlers.DatatypeEventHandler):
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
                oItemRef = db.getItem(sID, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    db.putItem(oItemRef, trans)
                else:
                    new_attr.value.remove(sID)
    
            # calculate removed references
            lstRemoved = list(prvValue - currentValue)
            for sID in lstRemoved:
                oItemRef = db.getItem(sID, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                db.putItem(oItemRef, trans)
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes

            lstValue = attr.value
            if lstValue and attr.respectsReferences:
                raise serverExceptions.ReferentialIntegrityError
            
            # remove references
            for sID in lstValue:
                oItemRef = db.getItem(sID, trans)
                if oItemRef.getContentclass() in attr.relCc:
                    oAttrRef = getattr(oItemRef, attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        try:
                            oAttrRef.value.remove(item._id)
                        except ValueError:
                            pass
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = ''
                    db.putItem(oItemRef, trans)
                else:
                    attr.value.remove(sID)
    
    @staticmethod
    def getNoAccessIds(attr, trans):
        lstNoAccess = []
        for sID in attr.value:
            oItem = dbEnv.getItem(sID, trans)
            # do not replay in case of txn abort
            del trans.actions[-1]
            
            if not(oItem):
                lstNoAccess.append(sID)
        return lstNoAccess
    
class Relator1EventHandler(eventHandlers.DatatypeEventHandler):
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
                oItemRef = db.getItem(new_attr.value, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    db.putItem(oItemRef, trans)
                else:
                    new_attr.value = ''
            if prvValue:
                oItemRef = db.getItem(prvValue, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                db.putItem(oItemRef, trans)

    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes
            if attr.value:
                if attr.respectsReferences:
                    raise serverExceptions.ReferentialIntegrityError
                # remove reference
                oItemRef = db.getItem(attr.value, trans)
                oAttrRef = getattr(oItemRef, attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                db.putItem(oItemRef, trans)

class ExternalAttributeEventHandler(eventHandlers.DatatypeEventHandler):
    "External attribute event handler"

    @staticmethod
    def on_create(item, attr, trans):
        ExternalAttributeEventHandler.on_update(item, attr, None, trans)
    
    @staticmethod
    def on_update(item, new_attr, old_attr, trans):
        if new_attr.isDirty:
            db.db_handle._putExternalAttribute(new_attr._id, new_attr.value, trans)
        new_attr._reset()
    
    @staticmethod
    def on_delete(item, attr, trans, bPermanent):
        if bPermanent:
            db.db_handle._deleteExternalAttribute(attr._id, trans)

