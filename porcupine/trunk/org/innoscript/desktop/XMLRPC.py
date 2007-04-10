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
"XMLRPC Servlets"

import os, os.path, base64

from porcupine.core.servlet import XMLRPCServlet
from porcupine.oql.command import OqlCommand
from porcupine.security import objectAccess
from porcupine.security.policy import policymethod
from porcupine import datatypes
from porcupine.utils import misc, date

from org.innoscript.desktop.strings import resources

#================================================================================
# Item Generic methods
#================================================================================

class ItemGeneric(XMLRPCServlet):
    def update(self, data):
        # get user role
        iUserRole = objectAccess.getAccess(self.item, self.session.user)
        if data.has_key('__rolesinherited') and iUserRole == objectAccess.COORDINATOR:
            self.item.inheritRoles = data.pop('__rolesinherited')
            if not self.item.inheritRoles:
                acl = data.pop('__acl')
                if acl:
                    security = {}
                    for descriptor in acl:
                        security[descriptor['id']] = int(descriptor['role'])
                    self.item.security = security

        for prop in data:
            oAttr = getattr(self.item, prop)
            if isinstance(oAttr, datatypes.File):
                # see if the user has uploaded a new file
                if data[prop]['tempfile']:
                    oAttr.filename = data[prop]['filename']
                    sPath = self.server.temp_folder + '/' + data[prop]['tempfile']
                    oAttr.loadFromFile(sPath)
                    os.remove(sPath)
            else:
                oAttr.value = data[prop]
        txn = self.server.store.getTransaction()
        self.item.update(txn)
        txn.commit()
        return True
        
    def copyTo(self, targetid):
        txn = self.server.store.getTransaction()
        self.item.copyTo(targetid, txn)
        txn.commit()
        return True
        
    def moveTo(self, targetid):
        txn = self.server.store.getTransaction()
        self.item.moveTo(targetid, txn)
        txn.commit()
        return True
        
    def rename(self, newName):
        txn = self.server.store.getTransaction()
        self.item.displayName.value = newName
        self.item.update(txn)
        txn.commit()
        return True
        
    def delete(self):
        txn = self.server.store.getTransaction()
        self.item.recycle('rb', txn)
        txn.commit()
        return True
        
    def getSecurity(self):
        l = []
        store = self.server.store
        for sID in self.item.security:
            oUser = store.getItem(sID)
            l.append(
                {
                    'id': sID,
                    'displayName': oUser.displayName.value,
                    'role': str(self.item.security[sID])
                }
            )
        return(l)

#================================================================================
# Container Generic methods
#================================================================================

class ContainerGeneric(ItemGeneric):
    def create(self, data):
        # create new item
        oNewItem = misc.getCallableByName(data.pop('CC'))()

        # get user role
        iUserRole = objectAccess.getAccess(self.item, self.session.user)
        if data.has_key('__rolesinherited') and iUserRole == objectAccess.COORDINATOR:
            oNewItem.inheritRoles = data.pop('__rolesinherited')
            if not oNewItem.inheritRoles:
                acl = data.pop('__acl')
                if acl:
                    security = {}
                    for descriptor in acl:
                        security[descriptor['id']] = int(descriptor['role'])
                    oNewItem.security = security

        # set props
        for prop in data:
            oAttr = getattr(oNewItem, prop)
            if isinstance(oAttr, datatypes.File):
                if data[prop]['tempfile']:
                    oAttr.filename = data[prop]['filename']
                    sPath = self.server.temp_folder + '/' + data[prop]['tempfile']
                    oAttr.loadFromFile(sPath)
                    os.remove(sPath)
            elif isinstance(oAttr, datatypes.Date):
                oAttr.value = data[prop].value
            else:
                oAttr.value = data[prop]
                
        txn = self.server.store.getTransaction()
        oNewItem.appendTo(self.item.id, txn)
        txn.commit()
        return True
        
    def getSubtree(self):
        sLang = self.request.getLang()
        l = []
        folders = self.item.getSubFolders()
        for folder in folders:
            o = {
                'id' : folder.id,
                'caption' : folder.displayName.value,
                'img' : folder.__image__,
                'haschildren' : folder.hasSubfolders()
            }
            l.append(o)
        return l

    def getInfo(self):
        sLang = self.request.getLang()
        lstChildren = []
        children = self.item.getChildren()
        for child in children:
            obj = {
                'id' : child.id,
                'image': child.__image__,
                'displayName' : child.displayName.value,
                'isCollection': child.isCollection,
                'modified': date.Date(child.modified)
            }
            if hasattr(child, 'size'):
                obj['size'] = child.size
            lstChildren.append(obj)
        
        containment = []
        for contained in self.item.containment:
            image = misc.getCallableByName(contained).__image__
            if not type(image)==str:
                image = ''
            localestring = resources.getResource(contained, sLang)
            containment.append( [localestring, contained, image] )
            
        return {
            'displayName': self.item.displayName.value,
            'path': misc.getFullPath(self.item),
            'parentid': self.item.parentid,
            'iscollection': self.item.isCollection,
            'containment': containment,
            'user_role': objectAccess.getAccess(self.item, self.session.user),
            'contents': lstChildren
        }

#================================================================================
# Root Folder
#================================================================================

class RootFolder(ContainerGeneric):
    def executeOqlCommand(self, command, range=None):
        oCmd = OqlCommand()
        oRes = oCmd.execute(command)
        if not range:
            retVal = [rec for rec in oRes]
            return(retVal)
        else:
            total_recs = len(oRes)
            slice = [ rec for rec in oRes[range[0]:range[1]] ]
            return [ slice,total_recs ]

    @policymethod('uploadpolicy')
    def upload(self, chunk, fname):
        chunk = base64.decodestring(chunk)
        if not fname:
            fileno, fname = self.session.getTempFile()
            os.write(fileno, chunk)
            os.close(fileno)
            fname = os.path.basename(fname)
        else:
            tmpfile = file(self.server.temp_folder + '/' + fname, 'ab+')
            tmpfile.write( chunk )
            tmpfile.close()
        return fname
    
    def logoff(self):
        self.session.terminate()
        return True

class Login(XMLRPCServlet):
    def login(self, username, password):
        self.runAsSystem()
        oUser = self.server.store.getItem('users').getChildByName(username)
        if oUser and hasattr(oUser, 'authenticate'):
            if oUser.authenticate(password):
                self.session.user = oUser
                return True
        return False
        
class ApplyUserSettings(XMLRPCServlet):
    def applySettings(self, data):
        activeUser = self.session.user
        self.runAsSystem()
        
        activeUser.settings.value = data
        
        txn = self.server.store.getTransaction()
        activeUser.update(txn)
        txn.commit()
        
        return True

#================================================================================
# Category
#================================================================================

class Category(ContainerGeneric):
    def getInfo(self):
        info = ContainerGeneric.getInfo(self)
        lstObjects = []
        category_objects = self.item.category_objects.getItems()
        for item in category_objects:
            obj = {
                'id' : item.id,
                'image': item.__image__,
                'displayName' : item.displayName.value,
                'isCollection': item.isCollection,
                'modified': date.Date(item.modified)
            }
            if hasattr(item, 'size'):
                obj['size'] = item.size
            lstObjects.append(obj)
        info['contents'].extend(lstObjects)
        return info

#================================================================================
# Recycle Bin
#================================================================================

class RecycleBin(ContainerGeneric):
    def getInfo(self):
        sLang = self.request.getLang()
        lstChildren = []
        children = self.item.getChildren()
        for child in children:
            obj = {
                'id' : child.id,
                'image': child.__image__,
                'displayName' : child.originalName,
                'origloc': child.originalLocation,
                'modified': date.Date(child.modified)
            }
            if hasattr(child, 'size'):
                obj['size'] = child.size
            lstChildren.append(obj)
        return {
            'displayName': self.item.displayName.value,
            'contents': lstChildren
        }
        
    def empty(self):
        txn = self.server.store.getTransaction()
        self.item.empty(txn)
        txn.commit()
        return True

#================================================================================
# Users and groups folder
#================================================================================

#================================================================================
# Deleted Item
#================================================================================

class DeletedItem(XMLRPCServlet):
    def restore(self):
        txn = self.server.store.getTransaction()
        self.item.restore(txn)
        txn.commit()
        return True
        
    def restoreTo(self, targetid):
        txn = self.server.store.getTransaction()
        self.item.restoreTo(targetid, txn)
        txn.commit()
        return True
        
    def delete(self):
        txn = self.server.store.getTransaction()
        self.item.delete(txn)
        txn.commit()
        return True

#================================================================================
# User     
#================================================================================

class User(ItemGeneric):
    def resetPassword(self, new_password):
        txn = self.server.store.getTransaction()
        self.item.password.value = new_password
        self.item.update(txn)
        txn.commit()
        return True
