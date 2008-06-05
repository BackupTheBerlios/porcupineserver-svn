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
System top-level Porcupine Objects.
Use these as base classes to create you own custom objects.

@see: L{org.innoscript.desktop.schema} module as a usage guideline.
"""

import time, copy
from threading import currentThread

from porcupine import db
from porcupine.db import _db
from porcupine.security import objectAccess
from porcupine import exceptions
from porcupine.core import objectSet
from porcupine.utils import misc
from porcupine import datatypes

class displayName(datatypes.String):
    """
    Porcupine object display name.
    
    All Porcupine objects have this attribute by default.
    Added in:
        1. L{GenericItem<porcupine.systemObjects.GenericItem>}
        2. L{Composite<porcupine.systemObjects.Composite>}
    """
    __slots__ = ()
    isRequired = True

#================================================================================
# Porcupine server top level classes
#================================================================================

class Cloneable(object):
    """
    Adds cloning capabilities to Porcupine Objects.
    
    Adding I{Cloneable} to the base classes of a class
    makes instances of this class cloneable, allowing item copying.
    """
    __slots__ = ()
    
    def _copy(self, target, trans, clearRolesInherited=False):
        oCopy = self.clone()
        if clearRolesInherited:
            oCopy.inheritRoles = False

        oUser = currentThread().context.session.user
        oCopy._owner = oUser._id
        oCopy._created = time.time()
        oCopy.modifiedBy = oUser.displayName.value
        oCopy.modified = time.time()
        oCopy._parentid = target._id
        
        _db.handle_update(oCopy, None, trans)
        _db.putItem(oCopy, trans)

        if self.isCollection:
            lstChildrentIds = self._items.values() + self._subfolders.values()
            for sId in lstChildrentIds:
                child = _db.getItem(sId, trans)
                if child and objectAccess.getAccess(child, oUser):
                    child._copy(oCopy, trans)

        target._addItemReference(oCopy)
        _db.putItem(target, trans)

    def clone(self):
        """
        Creates an in-memory clone of the item.
        This is a shallow copy operation meaning that the item's
        references are not cloned.
        
        @return: the clone object
        @rtype: type
        """
        oCopy = copy.deepcopy(self)
        oCopy._id = misc.generateOID()
        if self.isCollection:
            oCopy._subfolders = {}
            oCopy._items = {}
        return(oCopy)
    
    def copyTo(self, targetId, trans):
        """
        Copies the item to the designated target.

        @param targetId: The ID of the destination container
        @type targetId: str
        
        @param trans: A valid transaction handle 
            
        @return: None
        """
        oTarget = _db.getItem(targetId, trans)
        if self.isCollection and oTarget.isContainedIn(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot copy item to destination.\n' + \
                'The destination is contained in the source.'
        #check permissions on target folder
        oUser = currentThread().context.session.user
        iUserRole = objectAccess.getAccess(oTarget, oUser)
        if not(self._isSystem) and iUserRole>objectAccess.READER:
            if not(self.getContentclass() in oTarget.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % self.getContentclass()
            
            self._copy(oTarget, trans, True)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not copied.\n' + \
                'The user has insufficient permissions.'

class Moveable(object):
    """
    Adds moving capabilities to Porcupine Objects.
    
    Adding I{Moveable} to the base classes of a class
    makes instances of this class moveable, allowing item moving.
    """
    __slots__ = ()
    
    def moveTo(self, targetId, trans):
        """
        Moves the item to the designated target.
        
        @param targetId: The ID of the destination container
        @type targetId: str
        
        @param trans: A valid transaction handle 
            
        @return: None
        """
        oUser = currentThread().context.session.user
        iUserRole = objectAccess.getAccess(self, oUser)
        bCanMove = (iUserRole > objectAccess.AUTHOR)## or (iUserRole == objectAccess.AUTHOR and oItem.owner == oUser.id)

        parentId = self._parentid
        oTarget = _db.getItem(targetId, trans)
    
        iUserRole2 = objectAccess.getAccess(oTarget, oUser)
    
        if self.isCollection and oTarget.isContainedIn(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot move item to destination.\n' + \
                'The destination is contained in the source.'
    
        if (not(self._isSystem) and bCanMove and iUserRole2 > objectAccess.READER):
            if not(self.getContentclass() in oTarget.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % self.getContentclass()

            self._parentid = targetId
            self.inheritRoles = False
            _db.putItem(self, trans)

            #update target
            oTarget._addItemReference(self)
            _db.putItem(oTarget, trans)

            #update parent
            oParent = _db.getItem(parentId, trans)
            oParent._removeItemReference(self)
            _db.putItem(oParent, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not moved.\n' + \
                'The user has insufficient permissions.'

class Removeable(object):
    """
    Makes Porcupine objects removable.
    
    Adding I{Removeable} to the base classes of a class
    makes instances of this type removeable.
    Instances of this type can be either logically
    deleted - (moved to a L{RecycleBin} instance) - or physically
    deleted.
    """
    __slots__ = ()
    
    def _delete(self, trans):
        """
        Deletes the item physically.
        Bypasses security checks.
        
        Returns: None
        """
        _db.handle_delete(self, trans, True)
        _db.deleteItem(self, trans)
        
        if self.isCollection:
            lstChildren = self._items.values() + self._subfolders.values()
            for sID in lstChildren:
                oChild = _db.getItem(sID, trans)
                oChild._delete(trans)

    def delete(self, trans):
        """
        Deletes the item permanently.
        
        @param trans: A valid transaction handle 
        
        @return: None
        """
        oUser = currentThread().context.session.user
        self = _db.getItem(self._id, trans)

        iUserRole = objectAccess.getAccess(self, oUser)
        bCanDelete = (iUserRole > objectAccess.AUTHOR) or \
            (iUserRole == objectAccess.AUTHOR and self._owner == oUser._id)
        
        if (not(self._isSystem) and bCanDelete):
            # delete item physically
            self._delete(trans)
            # update container
            oParent = _db.getItem(self._parentid, trans)
            oParent._removeItemReference(self)
            _db.putItem(oParent, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not deleted.\n' + \
                'The user has insufficient permissions.'
    
    def _recycle(self, trans):
        """
        Removes an item's references and marks it as deleted.
        
        Returns: None
        """
        _db.handle_delete(self, trans, False)
        self._isDeleted = True
        
        if self.isCollection:
            lstChildren = self._items.values() + self._subfolders.values()
            for sID in lstChildren:
                oChild = _db.getItem(sID, trans)
                oChild._recycle(trans)
        
        _db.putItem(self, trans)

    def recycle(self, rbID, trans):
        """
        Moves the item to the specified recycle bin.
        
        The item then becomes inaccesible.
        
        @param rbID: The id of the destination container, which must be
                     a L{RecycleBin} instance
        @type rbID: str
        
        @param trans: A valid transaction handle 
        
        @return: None
        """
        oUser = currentThread().context.session.user
        self = _db.getItem(self._id, trans)
        
        iUserRole = objectAccess.getAccess(self, oUser)
        bCanDelete = (iUserRole > objectAccess.AUTHOR) or \
            (iUserRole == objectAccess.AUTHOR and self._owner == oUser._id)
        
        if (not(self._isSystem) and bCanDelete):
            oDeleted = DeletedItem(self)
            
            oDeleted._owner = oUser._id
            oDeleted._created = time.time()
            oDeleted.modifiedBy = oUser.displayName.value
            oDeleted.modified = time.time()
            oDeleted._parentid = rbID
            _db.handle_update(oDeleted, None, trans)
            _db.putItem(oDeleted, trans)
            
            # delete item logically
            self._recycle(trans)
            
            # save container
            oParent = _db.getItem(self._parentid, trans)
            oParent._removeItemReference(self)
            _db.putItem(oParent, trans)
            
            #update recycle bin
            oRecycleBin = _db.getItem(rbID, trans)
            if not(oDeleted.getContentclass() in oRecycleBin.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % oDeleted.getContentclass()
            oRecycleBin._addItemReference(oDeleted)
            _db.putItem(oRecycleBin, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not deleted.\n' + \
                'The user has insufficient permissions.'

class Composite(object):
    """Objects within Objects...
    
    Think of this as an embedded item. This class is usefull
    for implementing compositions. Instances of this class
    are embedded into other items.
    Note that instances of this class have no
    security descriptor since they are embedded into other items.
    The L{security} property of such instances is actually a proxy to
    the security attribute of the object that embeds this object.
    Moreover they do not have parent containers the way
    instances of L{GenericItem} have.

    @type contentclass: str
    @type id: str
    @type security: dict

    @see: L{porcupine.datatypes.Composition}.
    """
    __image__ = "desktop/images/object.gif"
    __slots__ = ('_id', '_containerid', '_isDeleted', 'displayName')
    __props__ = ()
    _eventHandlers = []

    def __init__(self):
        self._id = misc.generateOID()
        self._containerid = None
        self._isDeleted = False
        
        self.displayName = displayName()

    def getSecurity(self):
        """Getter of L{security} property
        
        @rtype: dict
        """
        return(_db.getItem(self._containerid).security)
    security = property(getSecurity)

    def getId(self):
        """Getter of L{id} property
        
        @rtype: str
        """
        return self._id
    id = property(getId)

    def getContentclass(self):
        """Getter of L{contentclass} property
        
        @rtype: str
        """
        return(self.__class__.__module__ + '.' + self.__class__.__name__)
    contentclass = property(getContentclass)

class GenericItem(object):
    """Generic Item
    The base class of all Poprcupine objects.
    
    @cvar __props__: A tuple containing all the object's custom data types.
    @type __props__: tuple

    @cvar _eventHandlers: A tuple containing all the object's custom data types.
    
    @ivar modifiedBy: The display name of the last modifier.
    @type modifiedBy: str
    
    @ivar modified: The last modification date, handled by the server.
    @type modified: float
    
    @ivar security: The object's security descriptor. This is a dictionary whose
                    keys are the users' IDs and the values are the roles.
    @type security: dict
    
    @ivar inheritRoles: Indicates if the object's security
                        descriptor is identical to this of its parent
    @type inheritRoles: bool
    
    @ivar displayName: The display name of the object.
    @type displayName: L{displayName<porcupine.systemObjects.displayName>}
    
    @ivar description: A short description.
    @type description: L{String<porcupine.datatypes.String>}
    
    @type contentclass: str
    @type created: float
    @type id: str
    @type isCollection: bool
    @type isSystem: bool
    @type owner: type
    @type parentid: str
    """
    __image__ = "desktop/images/object.gif"
    __slots__ = (
        '_id', '_parentid', '_owner', '_isSystem', '_isDeleted',
        '_created', 'modifiedBy', 'modified', 'security', 'inheritRoles',
        'displayName', 'description'
    )
    __props__ = ('displayName', 'description')
    isCollection = property(lambda x:False, None, None,
                    "Indicates if this object is a container.")
    _eventHandlers = []

    def __init__(self):
        # system props
        self._id = misc.generateOID()
        self._parentid = ''
        self._owner = ''
        self._isSystem = False
        self._isDeleted = False
        self._created = 0
        
        self.modifiedBy = ''
        self.modified = 0
        self.security = {}
        self.inheritRoles = True

        self.displayName = displayName()
        self.description = datatypes.String()

    def _applySecurity(self, oParent, trans):
        if self.inheritRoles:
            self.security = oParent.security
        if self.isCollection:
            for sID in self._subfolders.values() + self._items.values():
                oItem = _db.getItem(sID, trans)
                if oItem.inheritRoles:
                    oItem._applySecurity(self, trans)
                    _db.putItem(oItem, trans)

    def appendTo(self, parent, trans):
        """
        Adds the item to the specified container.

        @param parent: The id of the destination container or the container
            itself
        @type parent: str OR L{Container}
        
        @param trans: A valid transaction handle
        
        @return: None
        """
        if type(parent)==str:
            oParent = _db.getItem(parent, trans)
        else:
            oParent = parent
        
        oUser = currentThread().context.session.user
        iUserRole = objectAccess.getAccess(oParent, oUser)
        if iUserRole == objectAccess.READER:
            raise exceptions.PermissionDenied, \
                'The user does not have write permissions ' + \
                'on the parent folder.'
        if not(self.getContentclass() in oParent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type "%s".' % self.getContentclass()

        # set security to new item
        if iUserRole == objectAccess.COORDINATOR:
            # user is COORDINATOR
            self._applySecurity(oParent, trans)
        else:
            # user is not COORDINATOR
            self.inheritRoles = True
            self.security = oParent.security
            #if trans._retries == 0:
            #   raise exceptions.DBTransactionIncomplete    
        self._owner = oUser._id
        self._created = time.time()
        self.modifiedBy = oUser.displayName.value
        self.modified = time.time()
        self._parentid = oParent._id
        _db.handle_update(self, None, trans)
        _db.putItem(self, trans)
        # update container
        oParent._addItemReference(self)
        _db.putItem(oParent, trans)

    def isContainedIn(self, itemId, trans=None):
        """
        Checks if the item is contained in the specified container.
        
        @param itemId: The id of the container
        @type itemId: str
        
        @rtype: bool
        """
        oItem = self
        while oItem._id is not '':
            if oItem._id==itemId:
                return True
            oItem = _db.getItem(oItem.parentid, trans)
        return False

    def getParent(self, trans=None):
        """
        Returns the parent container.
                
        @param trans: A valid transaction handle
            
        @return: the parent container object
        @rtype: type
        """
        return(db.getItem(self._parentid, trans))

    def getAllParents(self, trans=None):
        """
        Returns all the parents of the item traversing the
        hierarchy up to the root folder.
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        parents = []
        oItem = self
        while oItem and oItem._id:
            parents.append(oItem)
            oItem = oItem.getParent(trans)
        parents.reverse()
        return(objectSet.ObjectSet(parents))

    def getContentclass(self):
        """Getter of L{contentclass} property
        
        @rtype: str
        """
        return(self.__class__.__module__ + '.' + self.__class__.__name__)
    contentclass = property(getContentclass, None, None, "The type of the object")

    def getId(self):
        """Getter of L{id} property
        
        @rtype: str
        """
        return self._id
    id = property(getId, None, None, "The ID of the object")

    def getIsSystem(self):
        """Getter of L{isSystem} property
        
        @rtype: bool
        """
        return self._isSystem        
    isSystem = property(getIsSystem, None, None,
                        "Indicates if this is a system object")

    def getOwner(self):
        """Getter of L{owner} property
        
        @rtype: type
        """
        return self._owner
    owner = property(getOwner, None, None,
                        "The object creator")

    def getCreated(self):
        """Getter of L{created} property
        
        @rtype: float
        """
        return self._created
    created = property(getCreated, None, None,
                        "The creation date")

    def getParentId(self):
        """Getter of L{parentid} property
        
        @rtype: str
        """
        return self._parentid
    parentid = property(getParentId, None, None,
                        "The ID of the parent container")

#================================================================================
# Porcupine server system classes
#================================================================================

class DeletedItem(GenericItem, Removeable):
    """
    This is the type of items appended into a L{RecycleBin} class instance.
    
    L{RecycleBin} containers accept objects of this type only.
    Normally, you won't ever need to instantiate an item of this
    type. Instantiations of this class are handled by the server
    internally when the L{Removeable.recycle} method is called.
    
    @ivar originalName: The display name of the deleted object.
    @type originalName: str
    
    @ivar originalLocation: The path to the location of the deleted item
                             before the deletion
    @type originalLocation: str
    """
    __slots__ = ('_deletedId', '__image__', 'originalLocation','originalName')
    
    def __init__(self, deletedItem):
        GenericItem.__init__(self)

        self.inheritRoles = True
        self._deletedId = deletedItem._id
        self.__image__ = deletedItem.__image__
        
        self.displayName.value = misc.generateOID()
        self.description.value = deletedItem.description.value
        
        parents = deletedItem.getAllParents()
        sPath = '/'
        sPath += '/'.join([p.displayName.value for p in parents[:-1]])
        self.originalLocation = sPath
        self.originalName = deletedItem.displayName.value

    def _undelete(self, deletedItem, trans):
        """
        Undeletes a logically deleted item.
        
        Returns: None
        """
        _db.handle_update(deletedItem, None, trans)
        deletedItem._isDeleted = False
        
        if deletedItem.isCollection:
            lstChildren = deletedItem._items.values() + deletedItem._subfolders.values()
            for sID in lstChildren:
                oChild = _db.getDeletedItem(sID, trans)
                self._undelete(oChild, trans)

        _db.putItem(deletedItem, trans)

    def _restore(self, deletedItem, target, trans):
        """
        Restores a logically deleted item to the designated target.
        
        Returns: None
        """
        # check permissions
        oUser = currentThread().context.session.user
        iUserRole = objectAccess.getAccess(target, oUser)
        
        if iUserRole > objectAccess.READER:
            deletedItem._parentid = target._id
            deletedItem.inheritRoles = False
            self._undelete(deletedItem, trans)
        else:
            raise exceptions.PermissionDenied, \
                    'The user does not have write permissions on the ' + \
                    'destination folder.'

    def getDeletedItem(self):
        """
        Use this method to get the item that was logically deleted.
            
        @return: the deleted item
        @rtype: type
        """
        oDeleted = _db.getDeletedItem(self._deletedId)
        return(oDeleted)

    def appendTo(self, *args):
        """
        Calling this method raises an ContainmentError.
        This is happening because you can not add a DeletedItem
        directly to the store.
        This type of item is appended to the store only if
        the L{Removeable.recycle} method is called.

        @warning: DO NOT USE.
        @raise L{porcupine.exceptions.ContainmentError}: Always
        """
        raise exceptions.ContainmentError, \
            'Cannot directly add this item to the store.\n' + \
            'Use the "recycle" method instead.'

    def restore(self, trans):
        """
        Restores the deleted item to its original location, if
        it still exists.
        
        @param trans: A valid transaction handle
        
        @return: None
        
        @raise L{porcupine.exceptions.ObjectNotFound}:
            If the original location no longer exists.
        """
        ## TODO: check if oDeleted exists
        oDeleted = _db.getDeletedItem(self._deletedId, trans)
        oOriginalParent = _db.getItem(oDeleted._parentid, trans)
        
        # try to restore original item
        self._restore(oDeleted, oOriginalParent, trans)

        self.delete(trans, False)
        
        # update container
        oOriginalParent._addItemReference(oDeleted)
        _db.putItem(oOriginalParent, trans)
    
    def restoreTo(self, sParentId, trans):
        """
        Restores the deleted object to the specified container.
        
        @param sParentId: The ID of the container in which
            the item will be restored
        @type sParentId: str    
        
        @param trans: A valid transaction handle
            
        @return: None
        """
        ## TODO: check if oDeleted exists
        oDeleted = _db.getDeletedItem(self._deletedId, trans)
        oParent = _db.getItem(sParentId, trans)
        
        if not(oDeleted.getContentclass() in oParent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type "%s".' % oDeleted.getContentclass()
        
        # try to restore original item
        self._restore(oDeleted, oParent, trans)
        
        self.delete(trans, False)
        
        # update container
        oParent._addItemReference(oDeleted)
        _db.putItem(oParent, trans)

    def delete(self, trans, _removeDeleted=True):
        """
        Deletes the deleted object permanently.
        
        @param trans: A valid transaction handle
        @param _removeDeleted: Leave as is
            
        @return: None
        """
        Removeable.delete(self, trans)
        if _removeDeleted:
            # we got a direct call. remove deleted item
            ## TODO: check if oDeleted exists
            oDeleted = _db.getDeletedItem(self._deletedId, trans)
            _db.removeDeletedItem(oDeleted, trans)
        #else:
            # we got a call from "restore" or "restoreTo"
            # do not replay in case of txn abort
        #    del trans.actions[-1]

class Item(GenericItem, Cloneable, Moveable, Removeable):
    """
    Simple item with no versioning capabilities.
    
    Normally this is the base class of your custom Porcupine Objects
    if versioning is not required.
    Subclass the L{porcupine.systemObjects.Container} class if you want
    to create custom containers.
    """
    __slots__ = ()
    
    def __init__(self):
        GenericItem.__init__(self)

    def update(self, trans):
        """
        Updates the item.
        
        @param trans: A valid transaction handle
            
        @return: None
        """
        oOldItem = _db.getItem(self._id, trans)
        
        oUser = currentThread().context.session.user
        iUserRole = objectAccess.getAccess(oOldItem, oUser)
        
        if iUserRole > objectAccess.READER:
            # set security
            if iUserRole == objectAccess.COORDINATOR:
                # user is COORDINATOR
                if (self.inheritRoles != oOldItem.inheritRoles) or \
                (not self.inheritRoles and self.security != oOldItem.security):
                    oParent = _db.getItem(self._parentid, trans)
                    self._applySecurity(oParent, trans)
            else:
                # restore previous ACL
                self.security = oOldItem.security
                self.inheritRoles = oOldItem.inheritRoles

            _db.handle_update(self, oOldItem, trans)
            self.modifiedBy = oUser.displayName.value
            self.modified = time.time()
            _db.putItem(self, trans)
            
            if self.displayName.value != oOldItem.displayName.value:
                oParent = _db.getItem(self._parentid, trans)
                oParent._removeItemReference(oOldItem)
                oParent._addItemReference(self)
                _db.putItem(oParent, trans)
        else:
            raise exceptions.PermissionDenied, \
                    'The user does not have update permissions.'

class Container(Item):
    """
    Generic container class.
    
    Base class for all containers. Containers do not support versionning.
    
    @cvar containment: a tuple of strings with all the content types of
        Porcupine objects that this class instance can accept.
    @type containment: tuple
    
    @type isCollection: bool
    """
    __image__ = "desktop/images/folder.gif"
    __slots__ = ('_subfolders','_items')
    containment = ()
    isCollection = property(lambda x:True)
    
    def __init__(self):
        Item.__init__(self)
        self._subfolders = {}
        self._items = {}
    
    def _removeItemReference(self, oItem):
        if oItem.isCollection:
            del self._subfolders[oItem.displayName.value]
        else:
            del self._items[oItem.displayName.value]

    def _addItemReference(self, oItem):            
        if self.childExists(oItem.displayName.value):
            raise exceptions.ContainmentError, \
                'Cannot create item "%s" in container "%s".\n' % \
                (oItem.displayName.value, self.displayName.value) + \
                'An item with the specified name already exists.'
        if oItem.isCollection:
            self._subfolders[oItem.displayName.value] = oItem._id
        else:
            self._items[oItem.displayName.value] = oItem._id
        
    def childExists(self, name):
        """
        Checks if a child with the specified name is contained
        in the container.
        
        @param name: The name of the child to check for
        @type name: str
            
        @rtype: bool
        """
        return(self._items.has_key(name) or self._subfolders.has_key(name))

    def getChildId(self, name):
        """
        Given a name this function returns the ID of the child.
        
        @param name: The name of the child
        @type name: str
            
        @return: The ID of the child if a child with the given name exists
                 else None.
        @rtype: str
        """
        if (self._items.has_key(name)):
            return(self._items[name])
        elif (self._subfolders.has_key(name)):
            return(self._subfolders[name])
        else:
            return(None)        

    def getChildByName(self, name, trans=None):
        """
        This method returns the child with the specified name.
        
        @param name: The name of the child
        @type name: str
        
        @param trans: A valid transaction handle
            
        @return: The child object if a child with the given name exists
                 else None.
        @rtype: type
        """
        if (self._items.has_key(name)):
            oChild = db.getItem(self._items[name], trans)
            return(oChild)
        elif (self._subfolders.has_key(name)):
            oChild = db.getItem(self._subfolders[name], trans)
            return(oChild)
        else:
            return(None)

    def getChildren(self, trans=None):
        """
        This method returns all the children of the container.
        
        @param trans: A valid transaction handle
            
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        children = self.getSubFolders(trans) + self.getItems(trans)
        return(children)

    def getItems(self, trans=None):
        """
        This method returns the children that are not containers.
        
        @param trans: A valid transaction handle
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        return objectSet.ObjectSet(self._items.values(),
                                   txn=trans,
                                   resolved=False)

    def getSubFolders(self, trans=None):
        """
        This method returns the children that are containers.
        
        @param trans: A valid transaction handle
            
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        return objectSet.ObjectSet(self._subfolders.values(),
                                   txn=trans,
                                   resolved=False)

    def hasChildren(self):
        """
        Checks if the container has at least one non-container child.
        
        @rtype: bool
        """
        return not(self._items=={})

    def hasSubfolders(self):
        """
        Checks if the container has at least one child container.
        
        @rtype: bool
        """
        return not(self._subfolders=={})

class RecycleBin(Container):
    """
    Recycle bin class.
    
    By default every I{RecycleBin} class instance is a system item.
    It cannot be deleted, copied, moved or recycled.
    """
    __image__ = "desktop/images/trashcan_empty8.gif"
    __slots__ = ()
    containment = ('porcupine.systemObjects.DeletedItem', )

    def __init__(self):
        Container.__init__(self)
        self._isSystem = True

    def empty(self, trans):
        """
        This method empties the recycle bin.
        
        What this method actually does is to call the
        L{DeletedItem.delete} method for every
        L{DeletedItem} instance contained in the bin.
        
        @param trans: A valid transaction handle
            
        @return: None
        """
        oItems = self.getItems()
        for deleted in oItems:
            deleted.delete(trans)
