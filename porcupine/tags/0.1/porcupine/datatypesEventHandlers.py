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

import os

from porcupine import serverExceptions
from porcupine.core import eventHandlers

class CompositionEventHandler(eventHandlers.DatatypeEventHandler):
    "Composition datatype event handler"
    
    @classmethod
    def on_create(self, item, attr, trans):
        if item._isDeleted:
            attr.value = [self.db.getDeletedItem(sID, trans) for sID in attr.value]
        CompositionEventHandler.on_update(item, attr, None, trans)
        
    @classmethod
    def on_update(self, item, new_attr, old_attr, trans):
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
            self.db.handle_update(dctObjects[sID], None, trans)
            dctObjects[sID]._isDeleted = False
            self.db.putItem(dctObjects[sID], trans)
            
        # calculate constant composites
        lstConstant = list(new_ids & old_ids)
        for sID in lstConstant:
            self.db.handle_update(dctObjects[sID], db.getItem(sID, trans) , trans)
            self.db.putItem(dctObjects[sID], trans)

        # calculate removed composites
        lstRemoved = list(old_ids - new_ids)
        for sID in lstRemoved:
            composite4removal = self.db.getItem(sID, trans)
            self.removeComposite(composite4removal, trans)
            
        new_attr.value = list(new_ids)
    
    @classmethod
    def on_delete(self, item, attr, trans, bPermanent):
        if bPermanent:
            if item._isDeleted:
                func_get = self.db.getDeletedItem
            else:
                func_get = self.db.getItem
            composites = [func_get(sID, trans) for sID in attr.value]
            for composite in composites:
                self.removeComposite(composite, trans)
        else:
            for sID in attr.value:
                composite = self.db.getItem(sID, trans)
                self.db.handle_delete(composite, trans, False)
                composite._isDeleted = True
                self.db.putItem(composite, trans)
    
    @classmethod
    def removeComposite(self, composite, trans):
        self.db.handle_delete(composite, trans, True)
        self.db.deleteItem(composite, trans)
        
class RelatorNEventHandler(eventHandlers.DatatypeEventHandler):
    "RelatorN datatype event handler"
    
    @classmethod
    def on_create(self, item, attr, trans):
        RelatorNEventHandler.on_update(item, attr, None, trans)
    
    @classmethod
    def on_update(self, item, new_attr, old_attr, trans):
        from porcupine import datatypes
        # remove duplicates
        new_attr.value = list(set(new_attr.value))
        
        # get previous value
        if old_attr:
            prvValue = set(old_attr.value)
            noAccessList = self.getNoAccessIds(old_attr, trans)
        else:
            prvValue = set()
            noAccessList = []

        # get current value
        currentValue = set(new_attr.value + noAccessList)

        if currentValue != prvValue:
            # calculate added references
            lstAdded = list(currentValue - prvValue)
            for sID in lstAdded:
                oItemRef = self.db.getItem(sID, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    self.db.putItem(oItemRef, trans)
                else:
                    new_attr.value.remove(sID)
    
            # calculate removed references
            lstRemoved = list(prvValue - currentValue)
            for sID in lstRemoved:
                oItemRef = self.db.getItem(sID, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                self.db.putItem(oItemRef, trans)
    
    @classmethod
    def on_delete(self, item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes

            lstValue = attr.value
            if lstValue and attr.respectsReferences:
                raise serverExceptions.ReferentialIntegrityError
            
            # remove references
            for sID in lstValue:
                oItemRef = self.db.getItem(sID, trans)
                if oItemRef.getContentclass() in attr.relCc:
                    oAttrRef = getattr(oItemRef, attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        try:
                            oAttrRef.value.remove(item._id)
                        except ValueError:
                            pass
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = ''
                    self.db.putItem(oItemRef, trans)
                else:
                    attr.value.remove(sID)
    
    @classmethod
    def getNoAccessIds(self, attr, trans):
        lstNoAccess = []
        for sID in attr.value:
            oItem = self.store.getItem(sID, trans)
            # do not replay in case of txn abort
            del trans.actions[-1]
            
            if not(oItem):
                lstNoAccess.append(sID)
        return lstNoAccess
    
class Relator1EventHandler(eventHandlers.DatatypeEventHandler):
    "Relator1 datatype event handler"

    @classmethod
    def on_create(self, item, attr, trans):
        Relator1EventHandler.on_update(item, attr, None, trans)
 
    @classmethod
    def on_update(self, item, new_attr, old_attr, trans):
        from porcupine import datatypes
        
        # get previous value
        if old_attr:
            prvValue = old_attr.value
        else:
            prvValue = ''
        
        if new_attr.value != prvValue:
            if new_attr.value:
                oItemRef = self.db.getItem(new_attr.value, trans)
                if oItemRef.getContentclass() in new_attr.relCc:
                    oAttrRef = getattr(oItemRef, new_attr.relAttr)
                    if isinstance(oAttrRef, datatypes.RelatorN):
                        oAttrRef.value.append(item._id)
                    elif isinstance(oAttrRef, datatypes.Relator1):
                        oAttrRef.value = item._id
                    self.db.putItem(oItemRef, trans)
                else:
                    new_attr.value = ''
            if prvValue:
                oItemRef = self.db.getItem(prvValue, trans)
                oAttrRef = getattr(oItemRef, new_attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                self.db.putItem(oItemRef, trans)

    @classmethod
    def on_delete(self, item, attr, trans, bPermanent):
        if not item._isDeleted:
            from porcupine import datatypes
            if attr.value:
                if attr.respectsReferences:
                    raise serverExceptions.ReferentialIntegrityError
                # remove reference
                oItemRef = self.db.getItem(attr.value, trans)
                oAttrRef = getattr(oItemRef, attr.relAttr)
                if isinstance(oAttrRef, datatypes.RelatorN):
                    try:
                        oAttrRef.value.remove(item._id)
                    except ValueError:
                        pass
                elif isinstance(oAttrRef, datatypes.Relator1):
                    oAttrRef.value = ''
                self.db.putItem(oItemRef, trans)

class ExternalAttributeEventHandler(eventHandlers.DatatypeEventHandler):
    "External attribute event handler"

    @classmethod
    def on_create(self, item, attr, trans):
        ExternalAttributeEventHandler.on_update(item, attr, None, trans)
    
    @classmethod
    def on_update(self, item, new_attr, old_attr, trans):
        if new_attr.isDirty:
            self.db.db_handle._putExternalAttribute(new_attr._id, new_attr.value, trans)
        new_attr._reset()
    
    @classmethod
    def on_delete(self, item, attr, trans, bPermanent):
        if bPermanent:
            self.db.db_handle._deleteExternalAttribute(attr._id, trans)

class ExternalFileEventHandler(eventHandlers.DatatypeEventHandler):
    "External file event handler"
    
    @classmethod
    def on_delete(self, item, attr, trans, bPermanent):
        if bPermanent and attr.removeFileOnDeletion:
            try:
                os.remove(attr.value)
            except OSError:
                pass
