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
System top-level Porcupine content classes.
Use these as base classes to create you own custom objects.

@see: L{org.innoscript.desktop.schema} module as a usage guideline.
"""
import time
import copy
from threading import currentThread

from porcupine import db
from porcupine.db import _db
from porcupine import exceptions
from porcupine import datatypes
from porcupine.core.objectSet import ObjectSet
from porcupine.utils import misc
from porcupine.security import objectAccess

class displayName(datatypes.String):
    """Legacy data type. To be removed in the next version.
    Use L{porcupine.datatypes.RequiredString} instead.
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
    
    def _copy(self, target, trans, clear_inherited=False):
        clone = self.clone()
        if clear_inherited:
            clone.inheritRoles = False
        
        user = currentThread().context.user
        clone._owner = user._id
        clone._created = time.time()
        clone.modifiedBy = user.displayName.value
        clone.modified = time.time()
        clone._parentid = target._id
        
        _db.handle_update(clone, None, trans)
        _db.putItem(clone, trans)

        if self.isCollection:
            [child._copy(clone, trans) for child in self.getChildren(trans)]

    def clone(self, dup_ext_files=True):
        """
        Creates an in-memory clone of the item.
        This is a shallow copy operation meaning that the item's
        references are not cloned.
        
        @param dup_ext_files: Boolean indicating if the external
                files should be also duplicated
        @type dup_ext_files: bool
        
        @return: the clone object
        @rtype: type
        """
        clone = copy.deepcopy(self, {'df':dup_ext_files})
        clone._id = misc.generateOID()
        return(clone)
    
    def copyTo(self, target_id, trans):
        """
        Copies the item to the designated target.

        @param target_id: The ID of the destination container
        @type target_id: str
        
        @param trans: A valid transaction handle 
            
        @return: None
        """
        target = _db.getItem(target_id, trans)
        if self.isCollection and target.isContainedIn(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot copy item to destination.\n' + \
                'The destination is contained in the source.'
        
        #check permissions on target folder
        user = currentThread().context.user
        user_role = objectAccess.getAccess(target, user)
        if not(self._isSystem) and user_role > objectAccess.READER:
            if not(self.getContentclass() in target.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % self.getContentclass()
            
            self._copy(target, trans, clear_inherited=True)
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
    
    def moveTo(self, target_id, trans):
        """
        Moves the item to the designated target.
        
        @param target_id: The ID of the destination container
        @type target_id: str
        
        @param trans: A valid transaction handle 
            
        @return: None
        """
        user = currentThread().context.user
        user_role = objectAccess.getAccess(self, user)
        can_move = (user_role > objectAccess.AUTHOR)
        ## or (user_role == objectAccess.AUTHOR and oItem.owner == user.id)
        
        target = _db.getItem(target_id, trans)
        
        user_role2 = objectAccess.getAccess(target, user)
        
        if self.isCollection and target.isContainedIn(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot move item to destination.\n' + \
                'The destination is contained in the source.'
        
        if (not(self._isSystem) and can_move and user_role2 > objectAccess.READER):
            if not(self.getContentclass() in target.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % self.getContentclass()
            
            self._parentid = target_id
            self.inheritRoles = False
            _db.putItem(self, trans)
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
        
        @param trans: A valid transaction handle
        
        @return: None
        """
        _db.handle_delete(self, trans, True)
        _db.deleteItem(self, trans)
        
        if self.isCollection:
            [child._delete(trans)
             for child in _db.query_index('_parentid', self._id,
                                          trans, fetch_all=True)]

    def delete(self, trans):
        """
        Deletes the item permanently.
        
        @param trans: A valid transaction handle 
        
        @return: None
        """
        user = currentThread().context.user
        self = _db.getItem(self._id, trans)

        user_role = objectAccess.getAccess(self, user)
        can_delete = (user_role > objectAccess.AUTHOR) or \
            (user_role == objectAccess.AUTHOR and self._owner == user._id)
        
        if (not(self._isSystem) and can_delete):
            # delete item physically
            self._delete(trans)
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
            [child._recycle(trans)
             for child in _db.query_index('_parentid', self._id,
                                          trans, fetch_all=True)]
        
        _db.putItem(self, trans)
        
    def _undelete(self, trans):
        """
        Undeletes a logically deleted item.
        
        @return: None
        """
        self._isDeleted = False
        
        if self.isCollection:
            [child._undelete(trans)
             for child in _db.query_index('_parentid', self._id,
                                          trans, fetch_all=True)] 
        
        _db.putItem(self, trans)

    def recycle(self, rb_id, trans):
        """
        Moves the item to the specified recycle bin.
        The item then becomes inaccesible.
        
        @param rb_id: The id of the destination container, which must be
                     a L{RecycleBin} instance
        @type rb_id: str
        
        @param trans: A valid transaction handle 
        
        @return: None
        """
        user = currentThread().context.user
        self = _db.getItem(self._id, trans)
        
        user_role = objectAccess.getAccess(self, user)
        can_delete = (user_role > objectAccess.AUTHOR) or \
                     (user_role == objectAccess.AUTHOR and
                      self._owner == user._id)
        
        if (not(self._isSystem) and can_delete):
            deleted = DeletedItem(self)
            deleted._owner = user._id
            deleted._created = time.time()
            deleted.modifiedBy = user.displayName.value
            deleted.modified = time.time()
            deleted._parentid = rb_id
            
            _db.handle_update(deleted, None, trans)
            _db.putItem(deleted, trans)
            
            # delete item logically
            self._recycle(trans)
                        
            #update recycle bin
            oRecycleBin = _db.getItem(rb_id, trans)
            if not(deleted.getContentclass() in oRecycleBin.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type "%s".' % deleted.getContentclass()
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
        
        self.displayName = datatypes.RequiredString()

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
        return '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
    contentclass = property(getContentclass)

class GenericItem(object):
    """Generic Item
    The base class of all Porcupine objects.
    
    @cvar __props__: A tuple containing all the object's custom data types.
    @type __props__: tuple

    @cvar _eventHandlers: A list containing all the object's event handlers.
    @type _eventHandlers: list

    @cvar isCollection: A boolean indicating if the object is a container.
    @type isCollection: bool
    
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
    @type displayName: L{RequiredString<porcupine.datatypes.RequiredString>}
    
    @ivar description: A short description.
    @type description: L{String<porcupine.datatypes.String>}
    
    @type contentclass: str
    @type created: float
    @type id: str
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
    isCollection = False
    _eventHandlers = []

    def __init__(self):
        # system props
        self._id = misc.generateOID()
        self._parentid = None
        self._owner = ''
        self._isSystem = False
        self._isDeleted = False
        self._created = 0
        
        self.modifiedBy = ''
        self.modified = 0
        self.security = {}
        self.inheritRoles = True

        self.displayName = datatypes.RequiredString()
        self.description = datatypes.String()

    def _applySecurity(self, oParent, trans):
        if self.inheritRoles:
            self.security = oParent.security
        if self.isCollection:
            for child in _db.query_index('_parentid', self._id, trans,
                                         fetch_all=True):
                child._applySecurity(self, trans)
                _db.putItem(child, trans) 

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
        
        user = currentThread().context.user
        user_role = objectAccess.getAccess(oParent, user)
        if user_role == objectAccess.READER:
            raise exceptions.PermissionDenied, \
                'The user does not have write permissions ' + \
                'on the parent folder.'
        if not(self.getContentclass() in oParent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type "%s".' % self.getContentclass()

        # set security to new item
        if user_role == objectAccess.COORDINATOR:
            # user is COORDINATOR
            self._applySecurity(oParent, trans)
        else:
            # user is not COORDINATOR
            self.inheritRoles = True
            self.security = oParent.security   
        self._owner = user._id
        self._created = time.time()
        self.modifiedBy = user.displayName.value
        self.modified = time.time()
        self._parentid = oParent._id
        _db.handle_update(self, None, trans)
        _db.putItem(self, trans)
    
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
        item = self
        while item and item._id:
            parents.append(item)
            item = item.getParent(trans)
        parents.reverse()
        return(ObjectSet(parents))
    
    def getContentclass(self):
        """Getter of L{contentclass} property
        
        @rtype: str
        """
        return(self.__class__.__module__ + '.' + self.__class__.__name__)
    contentclass = property(getContentclass, None, None,
                            "The type of the object")
    
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
    owner = property(getOwner, None, None, "The object creator")
    
    def getCreated(self):
        """Getter of L{created} property
        
        @rtype: float
        """
        return self._created
    created = property(getCreated, None, None, "The creation date")
    
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
    __slots__ = ('_deletedId', '__image__', 'originalLocation', 'originalName')
    
    def __init__(self, deletedItem):
        GenericItem.__init__(self)

        self.inheritRoles = True
        self._deletedId = deletedItem._id
        self.__image__ = deletedItem.__image__
        
        self.displayName.value = misc.generateOID()
        self.description.value = deletedItem.description.value
        
        parents = deletedItem.getAllParents()
        full_path = '/'
        full_path += '/'.join([p.displayName.value for p in parents[:-1]])
        self.originalLocation = full_path
        self.originalName = deletedItem.displayName.value

    def _restore(self, deleted, target, trans):
        """
        Restores a logically deleted item to the designated target.
        
        @return: None
        """
        # check permissions
        user = currentThread().context.user
        user_role = objectAccess.getAccess(target, user)
        
        if user_role > objectAccess.READER:
            deleted._parentid = target._id
            deleted.inheritRoles = False
            deleted._undelete(trans)
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
        deleted = _db.getItem(self._deletedId)
        return(deleted)

    def appendTo(self, *args, **kwargs):
        """
        Calling this method raises an ContainmentError.
        This is happening because you can not add a DeletedItem
        directly to the store.
        This type of item is added in the database only if
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
            If the original location or the original item no longer exists.
        """
        deleted = _db.getItem(self._deletedId, trans)
        if deleted == None:
            raise exceptions.ObjectNotFound, (
                'Cannot locate original item.\n' +
                'It seems that this item resided in a container\n' +
                'that has been permanently deleted.', False)
        original_parent = _db.getItem(deleted._parentid, trans)
        if original_parent == None or original_parent._isDeleted:
            raise exceptions.ObjectNotFound, (
                'Cannot locate target container.\n' +
                'It seems that this container is permanently deleted.', False)
                
        # try to restore original item
        self._restore(deleted, original_parent, trans)
        self.delete(trans, _removeDeleted=False)
    
    def restoreTo(self, parent_id, trans):
        """
        Restores the deleted object to the specified container.
        
        @param parent_id: The ID of the container in which
            the item will be restored
        @type parent_id: str    
        
        @param trans: A valid transaction handle
            
        @return: None
        
        @raise L{porcupine.exceptions.ObjectNotFound}:
            If the original location or the original item no longer exists.
        """
        deleted = _db.getItem(self._deletedId, trans)
        if deleted == None:
            raise exceptions.ObjectNotFound, (
                'Cannot locate original item.\n' +
                'It seems that this item resided in a container\n' +
                'that has been permanently deleted.', False)
        parent = _db.getItem(parent_id, trans)
        if parent == None or parent._isDeleted:
            raise exceptions.ObjectNotFound, (
                'Cannot locate target container.\n' +
                'It seems that this container is permanently deleted.', False)
        
        if not(deleted.getContentclass() in parent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type\n"%s".' % deleted.getContentclass()
        
        # try to restore original item
        self._restore(deleted, parent, trans)
        self.delete(trans, _removeDeleted=False)

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
            deleted = _db.getItem(self._deletedId, trans)
            if deleted != None:
                deleted._delete(trans)

class Item(GenericItem, Cloneable, Moveable, Removeable):
    """
    Simple item with no versioning capabilities.
    
    Normally this is the base class of your custom Porcupine Objects
    if versioning is not required.
    Subclass the L{porcupine.systemObjects.Container} class if you want
    to create custom containers.
    """
    __slots__ = ()
    
    def update(self, trans):
        """
        Updates the item.
        
        @param trans: A valid transaction handle
            
        @return: None
        """
        old_item = _db.getItem(self._id, trans)
        
        user = currentThread().context.user
        user_role = objectAccess.getAccess(old_item, user)
        
        if user_role > objectAccess.READER:
            # set security
            if user_role == objectAccess.COORDINATOR:
                # user is COORDINATOR
                if (self.inheritRoles != old_item.inheritRoles) or \
                (not self.inheritRoles and self.security != old_item.security):
                    oParent = _db.getItem(self._parentid, trans)
                    self._applySecurity(oParent, trans)
            else:
                # restore previous ACL
                self.security = old_item.security
                self.inheritRoles = old_item.inheritRoles

            _db.handle_update(self, old_item, trans)
            self.modifiedBy = user.displayName.value
            self.modified = time.time()
            _db.putItem(self, trans)
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
    __slots__ = ()
    containment = ()
    isCollection = True
    
    def childExists(self, name, trans=None):
        """
        Checks if a child with the specified name is contained
        in the container.
        
        @param name: The name of the child to check for
        @type name: str
        
        @param trans: A valid transaction handle
            
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('displayName', name))
        return _db.test_natural_join(conditions, trans)
    
    def getChildId(self, name, trans=None):
        """
        Given a name this function returns the ID of the child.
        
        @param name: The name of the child
        @type name: str
        
        @param trans: A valid transaction handle
            
        @return: The ID of the child if a child with the given name exists
                 else None.
        @rtype: str
        """
        child = self.getChildByName(name, trans)
        if child:
            return child._id
    
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
        conditions = (('_parentid', self._id), ('displayName', name))
        child = [x for x in _db.natural_join(conditions, trans)]
        if len(child) == 1:
            return child[0]
    
    def getChildren(self, trans=None):
        """
        This method returns all the children of the container.
        
        @param trans: A valid transaction handle
            
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        return _db.query_index('_parentid', self._id, trans)
    
    def getItems(self, trans=None):
        """
        This method returns the children that are not containers.
        
        @param trans: A valid transaction handle
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        conditions = (('_parentid', self._id), ('isCollection', False))
        return _db.natural_join(conditions, trans)
    
    def getSubFolders(self, trans=None):
        """
        This method returns the children that are containers.
        
        @param trans: A valid transaction handle
            
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        conditions = (('_parentid', self._id), ('isCollection', True))
        return _db.natural_join(conditions, trans)
    
    def hasChildren(self, trans=None):
        """
        Checks if the container has at least one non-container child.
        
        @param trans: A valid transaction handle
        
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('isCollection', False))
        return _db.test_natural_join(conditions, trans)
    
    def hasSubfolders(self, trans=None):
        """
        Checks if the container has at least one child container.
        
        @param trans: A valid transaction handle
        
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('isCollection', True))
        return _db.test_natural_join(conditions, trans)

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
        items = self.getItems(trans)
        [item.delete(trans) for item in items]
