#===============================================================================
#    Copyright 2005-2009, Tassos Koutsovassilis
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
from porcupine.utils import misc, permsresolver
from porcupine.core.decorators import deprecated

class _Shortcuts(datatypes.RelatorN):
    'Data type for keeping the shortcuts IDs that an object has'
    relCc = ('porcupine.systemObjects.Shortcut',)
    relAttr = 'target'
    cascadeDelete = True
    
class _TargetItem(datatypes.Relator1):
    'The object ID of the target item of the shortcut.'
    relCc = ('porcupine.systemObjects.Item',)
    relAttr = 'shortcuts'
    isRequired = True

#================================================================================
# Porcupine server top level content classes
#================================================================================

class Cloneable(object):
    """
    Adds cloning capabilities to Porcupine Objects.
    
    Adding I{Cloneable} to the base classes of a class
    makes instances of this class cloneable, allowing item copying.
    """
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
        _db.put_item(clone, trans)

        if self.isCollection:
            [child._copy(clone, trans) for child in self.get_children(trans)]

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
        clone._id = misc.generate_oid()
        return(clone)
    
    def copy_to(self, target_id, trans):
        """
        Copies the item to the designated target.

        @param target_id: The ID of the destination container
        @type target_id: str
        @param trans: A valid transaction handle
        @return: None
        @raise L{porcupine.exceptions.ObjectNotFound}:
            If the target container does not exist.
        """
        target = _db.get_item(target_id, trans)
        if target == None or target._isDeleted:
            raise exceptions.ObjectNotFound, (
                'The target container "%s" does not exist.' %
                target_id , False)
        
        if isinstance(self, Shortcut):
            contentclass = self.get_target_contentclass(trans)
        else:
            contentclass = self.get_contentclass()
        
        if self.isCollection and target.is_contained_in(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot copy item to destination.\n' + \
                'The destination is contained in the source.'
        
        # check permissions on target folder
        user = currentThread().context.user
        user_role = permsresolver.get_access(target, user)
        if not(self._isSystem) and user_role > permsresolver.READER:
            if not(contentclass in target.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type\n"%s".' % contentclass
            
            self._copy(target, trans, clear_inherited=True)
            # update parent
            target.modified = time.time()
            _db.put_item(target, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not copied.\n' + \
                'The user has insufficient permissions.'
    copyTo = deprecated(copy_to)

class Movable(object):
    """
    Adds moving capabilities to Porcupine Objects.
    
    Adding I{Movable} to the base classes of a class
    makes instances of this class movable, allowing item moving.
    """
    def move_to(self, target_id, trans):
        """
        Moves the item to the designated target.
        
        @param target_id: The ID of the destination container
        @type target_id: str
        @param trans: A valid transaction handle
        @return: None
        @raise L{porcupine.exceptions.ObjectNotFound}:
            If the target container does not exist.
        """
        user = currentThread().context.user
        user_role = permsresolver.get_access(self, user)
        can_move = (user_role > permsresolver.AUTHOR)
        ## or (user_role == permsresolver.AUTHOR and oItem.owner == user.id)

        parent_id = self._parentid
        target = _db.get_item(target_id, trans)
        if target == None or target._isDeleted:
            raise exceptions.ObjectNotFound, (
                'The target container "%s" does not exist.' %
                target_id , False)
        
        if isinstance(self, Shortcut):
            contentclass = self.get_target_contentclass(trans)
        else:
            contentclass = self.get_contentclass()
        
        user_role2 = permsresolver.get_access(target, user)
        
        if self.isCollection and target.is_contained_in(self._id, trans):
            raise exceptions.ContainmentError, \
                'Cannot move item to destination.\n' + \
                'The destination is contained in the source.'
        
        if (not(self._isSystem) and can_move and
                user_role2 > permsresolver.READER):
            if not(contentclass in target.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type\n"%s".' % contentclass
            
            self._parentid = target._id
            self.inheritRoles = False
            self.modified = time.time()
            _db.check_unique(self, None, trans)
            _db.put_item(self, trans)

            # update target
            target.modified = time.time()
            _db.put_item(target, trans)

            # update parent
            parent = _db.get_item(parent_id, trans)
            parent.modified = time.time()
            _db.put_item(parent, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not moved.\n' + \
                'The user has insufficient permissions.'
    moveTo = deprecated(move_to)

class Removable(object):
    """
    Makes Porcupine objects removable.
    
    Adding I{Removable} to the base classes of a class
    makes instances of this type removable.
    Instances of this type can be either logically
    deleted - (moved to a L{RecycleBin} instance) - or physically
    deleted.
    """
    def _delete(self, trans):
        """
        Deletes the item physically.
        
        @param trans: A valid transaction handle
        @return: None
        """
        _db.handle_delete(self, trans, True)
        _db.delete_item(self, trans)
        
        if self.isCollection:
            cursor = None
            try:
                cursor = _db.query_index('_parentid', self._id, trans)
                cursor.fetch_all = True
                [child._delete(trans) for child in cursor]
            finally:
                if cursor != None:
                    cursor.close()

    def delete(self, trans):
        """
        Deletes the item permanently.
        
        @param trans: A valid transaction handle
        @return: None
        """
        user = currentThread().context.user
        self = _db.get_item(self._id, trans)

        user_role = permsresolver.get_access(self, user)
        can_delete = (user_role > permsresolver.AUTHOR) or \
            (user_role == permsresolver.AUTHOR and self._owner == user._id)
        
        if (not(self._isSystem) and can_delete):
            # delete item physically
            self._delete(trans)
            # update container
            parent = _db.get_item(self._parentid, trans)
            parent.modified = time.time()
            _db.put_item(parent, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not deleted.\n' + \
                'The user has insufficient permissions.'
    
    def _recycle(self, trans):
        """
        Deletes an item logically.
        Bypasses security checks.
        
        @return: None
        """
        if not self._isDeleted:
            _db.handle_delete(self, trans, False)
        
        self._isDeleted = int(self._isDeleted) + 1
        
        if self.isCollection:
            cursor = None
            try:
                cursor = _db.query_index('_parentid', self._id, trans)
                cursor.fetch_all = True
                [child._recycle(trans) for child in cursor]
            finally:
                if cursor != None:
                    cursor.close()
        
        _db.put_item(self, trans)
        
    def _undelete(self, trans):
        """
        Undeletes a logically deleted item.
        Bypasses security checks.
        
        @return: None
        """
        if int(self._isDeleted) == 1:
            _db.handle_undelete(self, trans)
        
        self._isDeleted = int(self._isDeleted) - 1
        
        if self.isCollection:
            cursor = None
            try:
                cursor = _db.query_index('_parentid', self._id, trans)
                cursor.fetch_all = True
                [child._undelete(trans) for child in cursor]
            finally:
                if cursor != None:
                    cursor.close()
        
        _db.put_item(self, trans)

    def recycle(self, rb_id, trans):
        """
        Moves the item to the specified recycle bin.
        The item then becomes inaccessible.
        
        @param rb_id: The id of the destination container, which must be
                      a L{RecycleBin} instance
        @type rb_id: str
        @param trans: A valid transaction handle
        @return: None
        """
        user = currentThread().context.user
        self = _db.get_item(self._id, trans)
        
        user_role = permsresolver.get_access(self, user)
        can_delete = (user_role > permsresolver.AUTHOR) or \
                     (user_role == permsresolver.AUTHOR and
                      self._owner == user._id)
        
        if (not(self._isSystem) and can_delete):
            deleted = DeletedItem(self, trans)
            deleted._owner = user._id
            deleted._created = time.time()
            deleted.modifiedBy = user.displayName.value
            deleted.modified = time.time()
            deleted._parentid = rb_id
            
            # check recycle bin's containment
            recycle_bin = _db.get_item(rb_id, trans)
            if not(deleted.get_contentclass() in recycle_bin.containment):
                raise exceptions.ContainmentError, \
                    'The target container does not accept ' + \
                    'objects of type\n"%s".' % deleted.get_contentclass()
            
            _db.handle_update(deleted, None, trans)
            _db.put_item(deleted, trans)
            
            # delete item logically
            self._recycle(trans)
            
            # update container
            parent = _db.get_item(self._parentid, trans)
            parent.modified = time.time()
            _db.put_item(parent, trans)
        else:
            raise exceptions.PermissionDenied, \
                'The object was not deleted.\n' + \
                'The user has insufficient permissions.'

class Composite(object):
    """Objects within Objects...
    
    Think of this as an embedded item. This class is useful
    for implementing compositions. Instances of this class
    are embedded into other items.
    Note that instances of this class have no
    security descriptor since they are embedded into other items.
    The L{security} property of such instances is actually a proxy to
    the security attribute of the object that embeds this object.
    Moreover, they do not have parent containers the way
    instances of L{GenericItem} have.
    
    @type contentclass: str
    @type id: str
    @type security: dict
    @see: L{porcupine.datatypes.Composition}.
    """
    __image__ = "desktop/images/object.gif"
    __props__ = ()
    _eventHandlers = []

    def __init__(self):
        self._id = misc.generate_oid()
        self._containerid = None
        self._isDeleted = 0
        
        self.displayName = datatypes.RequiredString()

    def get_security(self):
        """Getter of L{security} property
        
        @rtype: dict
        """
        return(_db.get_item(self._containerid).security)
    security = property(get_security)

    def get_id(self):
        """Getter of L{id} property
        
        @rtype: str
        """
        return self._id
    id = property(get_id)

    def get_contentclass(self):
        """Getter of L{contentclass} property
        
        @rtype: str
        """
        return '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
    contentclass = property(get_contentclass)

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
    @type issystem: bool
    @type owner: type
    @type parentid: str
    """
    __image__ = "desktop/images/object.gif"
    __props__ = ('displayName', 'description')
    isCollection = False
    _eventHandlers = []

    def __init__(self):
        # system props
        self._id = misc.generate_oid()
        self._parentid = None
        self._owner = ''
        self._isSystem = False
        self._isDeleted = 0
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
            cursor = None
            try:
                cursor = _db.query_index('_parentid', self._id, trans)
                cursor.fetch_all = True
                for child in cursor:
                    child._applySecurity(self, trans)
                    _db.put_item(child, trans)
            finally:
                if cursor != None:
                    cursor.close()

    def append_to(self, parent, trans):
        """
        Adds the item to the specified container.

        @param parent: The id of the destination container or the container
                       itself
        @type parent: str OR L{Container}
        @param trans: A valid transaction handle
        @return: None
        """
        if type(parent) == str:
            parent = _db.get_item(parent, trans)
        
        if isinstance(self, Shortcut):
            contentclass = self.get_target_contentclass(trans)
        else:
            contentclass = self.get_contentclass()
        
        user = currentThread().context.user
        user_role = permsresolver.get_access(parent, user)
        if user_role == permsresolver.READER:
            raise exceptions.PermissionDenied, \
                'The user does not have write permissions ' + \
                'on the parent folder.'
        if not(contentclass in parent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type\n"%s".' % contentclass

        # set security to new item
        if user_role == permsresolver.COORDINATOR:
            # user is COORDINATOR
            self._applySecurity(parent, trans)
        else:
            # user is not COORDINATOR
            self.inheritRoles = True
            self.security = parent.security
        
        self._owner = user._id
        self._created = time.time()
        self.modifiedBy = user.displayName.value
        self.modified = time.time()
        self._parentid = parent._id
        _db.handle_update(self, None, trans)
        parent.modified = self.modified
        _db.put_item(self, trans)
        _db.put_item(parent, trans)
    appendTo = deprecated(append_to)
    
    def is_contained_in(self, item_id, trans=None):
        """
        Checks if the item is contained in the specified container.
        
        @param item_id: The id of the container
        @type item_id: str
        @rtype: bool
        """
        item = self
        while item._id != '':
            if item._id == item_id:
                return True
            item = _db.get_item(item.parentid, trans)
        return False
    isContainedIn = deprecated(is_contained_in)
    
    def get_parent(self, trans=None):
        """
        Returns the parent container.
                
        @param trans: A valid transaction handle
        @return: the parent container object
        @rtype: type
        """
        return db.get_item(self._parentid, trans)
    getParent = deprecated(get_parent)
    
    def get_all_parents(self, trans=None):
        """
        Returns all the parents of the item traversing the
        hierarchy up to the root folder.
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        parents = []
        item = self
        while item and item._id:
            parents.append(item)
            item = item.get_parent(trans)
        parents.reverse()
        return ObjectSet(parents)
    getAllParents = deprecated(get_all_parents)
    
    def get_contentclass(self):
        """Getter of L{contentclass} property
        
        @rtype: str
        """
        return(self.__class__.__module__ + '.' + self.__class__.__name__)
    contentclass = property(get_contentclass, None, None,
                            "The type of the object")
    
    def get_id(self):
        """Getter of L{id} property
        
        @rtype: str
        """
        return self._id
    id = property(get_id, None, None, "The ID of the object")
    
    def get_is_system(self):
        """Getter of L{issystem} property
        
        @rtype: bool
        """
        return self._isSystem
    issystem = property(get_is_system, None, None,
                        "Indicates if this is a systemic object")
    isSystem = property(deprecated(get_is_system, "issystem"), None, None,
                        "Deprecated property. Use issystem instead.")
    
    def get_owner(self):
        """Getter of L{owner} property
        
        @rtype: type
        """
        return self._owner
    owner = property(get_owner, None, None, "The object's creator")
    
    def get_created(self):
        """Getter of L{created} property
        
        @rtype: float
        """
        return self._created
    created = property(get_created, None, None, "The creation date")
    
    def get_parent_id(self):
        """Getter of L{parentid} property
        
        @rtype: str
        """
        return self._parentid
    parentid = property(get_parent_id, None, None,
                        "The ID of the parent container")

#================================================================================
# Porcupine server system classes
#================================================================================

class DeletedItem(GenericItem, Removable):
    """
    This is the type of items appended into a L{RecycleBin} class instance.
    
    L{RecycleBin} containers accept objects of this type only.
    Normally, you won't ever need to instantiate an item of this
    type. Instantiations of this class are handled by the server
    internally when the L{Removable.recycle} method is called.
    
    @ivar originalName: The display name of the deleted object.
    @type originalName: str
    @ivar originalLocation: The path to the location of the deleted item
                            before the deletion
    @type originalLocation: str
    """
    def __init__(self, deleted_item, trans=None):
        GenericItem.__init__(self)

        self.inheritRoles = True
        self._deletedId = deleted_item._id
        self.__image__ = deleted_item.__image__
        
        self.displayName.value = misc.generate_oid()
        self.description.value = deleted_item.description.value
        
        parents = deleted_item.get_all_parents(trans)
        full_path = '/'
        full_path += '/'.join([p.displayName.value for p in parents[:-1]])
        self.originalLocation = full_path
        self.originalName = deleted_item.displayName.value

    def _restore(self, deleted, target, trans):
        """
        Restores a logically deleted item to the designated target.
        
        @return: None
        """
        # check permissions
        user = currentThread().context.user
        user_role = permsresolver.get_access(target, user)
        
        if user_role > permsresolver.READER:
            deleted._parentid = target._id
            deleted.inheritRoles = False
            deleted._undelete(trans)
        else:
            raise exceptions.PermissionDenied, \
                    'The user does not have write permissions on the ' + \
                    'destination folder.'

    def get_deleted_item(self):
        """
        Use this method to get the item that was logically deleted.
            
        @return: the deleted item
        @rtype: L{GenericItem}
        """
        return _db.get_item(self._deletedId)
    getDeletedItem = deprecated(get_deleted_item)

    def append_to(self, *args, **kwargs):
        """
        Calling this method raises an ContainmentError.
        This is happening because you can not add a DeletedItem
        directly to the store.
        This type of item is added in the database only if
        the L{Removable.recycle} method is called.

        @warning: DO NOT USE.
        @raise L{porcupine.exceptions.ContainmentError}: Always
        """
        raise exceptions.ContainmentError, \
            'Cannot directly add this item to the store.\n' + \
            'Use the "recycle" method instead.'
    appendTo = deprecated(append_to)

    def restore(self, trans):
        """
        Restores the deleted item to its original location, if
        it still exists.
        
        @param trans: A valid transaction handle
        @return: None
        @raise L{porcupine.exceptions.ObjectNotFound}:
            If the original location or the original item no longer exists.
        """
        self.restore_to(None, trans)
        
    def restore_to(self, parent_id, trans):
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
        deleted = _db.get_item(self._deletedId, trans)
        if deleted == None:
            raise exceptions.ObjectNotFound, (
                'Cannot locate original item.\n' +
                'It seems that this item resided in a container\n' +
                'that has been permanently deleted or it is shortcut\n' +
                'having its target permanently deleted.', False)
        parent = _db.get_item(parent_id or deleted._parentid, trans)
        if parent == None or parent._isDeleted:
            raise exceptions.ObjectNotFound, (
                'Cannot locate target container.\n' +
                'It seems that this container is deleted.', False)
        
        if isinstance(deleted, Shortcut):
            contentclass = deleted.get_target_contentclass(trans)
        else:
            contentclass = deleted.get_contentclass()
        
        if contentclass and not(contentclass in parent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type\n"%s".' % contentclass
        
        # try to restore original item
        self._restore(deleted, parent, trans)
        # update parent
        parent.modified = time.time()
        _db.put_item(parent, trans)
        # delete self
        self.delete(trans, _removeDeleted=False)
    restoreTo = deprecated(restore_to)

    def delete(self, trans, _removeDeleted=True):
        """
        Deletes the deleted object permanently.
        
        @param trans: A valid transaction handle
        @param _removeDeleted: Leave as is
        @return: None
        """
        Removable.delete(self, trans)
        if _removeDeleted:
            # we got a direct call. remove deleted item
            deleted = _db.get_item(self._deletedId, trans)
            if deleted != None:
                deleted._delete(trans)

class Item(GenericItem, Cloneable, Movable, Removable):
    """
    Simple item with no versioning capabilities.
    
    Normally this is the base class of your custom Porcupine Objects
    if versioning is not required.
    Subclass the L{porcupine.systemObjects.Container} class if you want
    to create custom containers.
    """
    __props__ = GenericItem.__props__ + ('shortcuts',)
    
    def __init__(self):
        GenericItem.__init__(self)
        self.shortcuts = _Shortcuts()

    def update(self, trans):
        """
        Updates the item.
        
        @param trans: A valid transaction handle
        @return: None
        """
        old_item = _db.get_item(self._id, trans)
        parent = _db.get_item(self._parentid, trans)
        
        user = currentThread().context.user
        user_role = permsresolver.get_access(old_item, user)
        
        if user_role > permsresolver.READER:
            # set security
            if user_role == permsresolver.COORDINATOR:
                # user is COORDINATOR
                if (self.inheritRoles != old_item.inheritRoles) or \
                        (not self.inheritRoles and \
                         self.security != old_item.security):
                    self._applySecurity(parent, trans)
            else:
                # restore previous ACL
                self.security = old_item.security
                self.inheritRoles = old_item.inheritRoles

            _db.handle_update(self, old_item, trans)
            self.modifiedBy = user.displayName.value
            self.modified = time.time()
            parent.modified = self.modified
            _db.put_item(self, trans)
            _db.put_item(parent, trans)
        else:
            raise exceptions.PermissionDenied, \
                    'The user does not have update permissions.'

class Shortcut(Item):
    """
    Shortcuts act as pointers to other objects.
    
    When adding a shortcut in a container the containment
    is checked against the target's content class and not
    the shortcut's.
    When deleting an object that has shortcuts all its
    shortcuts are also deleted. Likewise, when restoring
    the object all of its shortcuts are also restored to
    their original location.
    It is valid to have shortcuts pointing to shortcuts.
    In order to resolve the terminal target object use the
    L{get_target} method.
    """
    __image__ = "desktop/images/link.png"
    __props__ = Item.__props__ + ('target',)
    
    def __init__(self):
        Item.__init__(self)
        self.target = _TargetItem()
        
    @staticmethod
    def create(target, trans=None):
        """Helper method for creating shortcuts of items.
        
        @param target: The id of the item or the item object itself
        @type parent: str OR L{Item}
        @param trans: A valid transaction handle
        @return: L{Shortcut}
        """
        if type(target) == str:
            target = _db.get_item(target, trans)
        shortcut = Shortcut()
        shortcut.displayName.value = target.displayName.value
        shortcut.target.value = target._id
        return shortcut
    
    def get_target(self, trans=None):
        """Returns the target item.
        
        @param trans: A valid transaction handle
        @return: the target item or C{None} if the user
                 has no read permissions
        @rtype: L{Item} or NoneType
        """
        target = None
        if self.target.value:
            target = self.target.get_item(trans)
            while target and isinstance(target, Shortcut):
                target = target.target.get_item(trans)
        return target
    
    def get_target_contentclass(self, trans=None):
        """Returns the content class of the target item.
        
        @param trans: A valid transaction handle
        @return: the fully qualified name of the target's
                 content class
        @rtype: str
        """
        if self.target.value:
            target = _db.get_item(self.target.value, trans)
            while isinstance(target, Shortcut):
                target = _db.get_item(target.target.value, trans)
            return target.get_contentclass()

class Container(Item):
    """
    Generic container class.
    
    Base class for all containers. Containers do not support versioning.
    
    @cvar containment: a tuple of strings with all the content types of
                       Porcupine objects that this class instance can accept.
    @type containment: tuple
    @type isCollection: bool
    """
    __image__ = "desktop/images/folder.gif"
    containment = ('porcupine.systemObjects.Shortcut',)
    isCollection = True
    
    def child_exists(self, name, trans=None):
        """
        Checks if a child with the specified name is contained
        in the container.
        
        @param name: The name of the child to check for
        @type name: str
        
        @param trans: A valid transaction handle
            
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('displayName', name))
        return _db.test_join(conditions, trans)
    childExists = deprecated(child_exists)
    
    def get_child_id(self, name, trans=None):
        """
        Given a name this function returns the ID of the child.
        
        @param name: The name of the child
        @type name: str
        @param trans: A valid transaction handle
        @return: The ID of the child if a child with the given name exists
                 else None.
        @rtype: str
        """
        conditions = (('_parentid', self._id), ('displayName', name))
        cursor = None
        try:
            cursor = _db.join(conditions, trans)
            cursor.use_primary = True
            iterator = iter(cursor)
            try:
                child = iterator.next()
            except StopIteration:
                child = None
            iterator.close()
        finally:
            if cursor != None:
                cursor.close()
        return child
    getChildId = deprecated(get_child_id)
    
    def get_child_by_name(self, name, trans=None):
        """
        This method returns the child with the specified name.
        
        @param name: The name of the child
        @type name: str
        @param trans: A valid transaction handle
        @return: The child object if a child with the given name exists
                 else None.
        @rtype: L{GenericItem}
        """
        conditions = (('_parentid', self._id), ('displayName', name))
        cursor = None
        iterator = None
        try:
            cursor = _db.join(conditions, trans)
            iterator = iter(cursor)
            try:
                child = iterator.next()
            except StopIteration:
                child = None
        finally:
            if iterator != None:
                iterator.close()
            if cursor != None:
                cursor.close()
        return child
    getChildByName = deprecated(get_child_by_name)
    
    def get_children(self, trans=None, resolve_shortcuts=False):
        """
        This method returns all the children of the container.
        
        @param trans: A valid transaction handle
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        cursor = None
        try:
            cursor = _db.query_index('_parentid', self._id, trans)
            cursor.resolve_shortcuts = resolve_shortcuts
            children = ObjectSet([c for c in cursor])
        finally:
            if cursor != None:
                cursor.close()
        return children
    getChildren = deprecated(get_children)
    
    def get_items(self, trans=None, resolve_shortcuts=False):
        """
        This method returns the children that are not containers.
        
        @param trans: A valid transaction handle
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        conditions = (('_parentid', self._id), ('isCollection', False))
        cursor = None
        try:
            cursor = _db.join(conditions, trans)
            cursor.resolve_shortcuts = resolve_shortcuts
            items = ObjectSet([i for i in cursor])
        finally:
            if cursor != None:
                cursor.close()
        return items
    getItems = deprecated(get_items)
    
    def get_subfolders(self, trans=None, resolve_shortcuts=False):
        """
        This method returns the children that are containers.
        
        @param trans: A valid transaction handle
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        conditions = (('_parentid', self._id), ('isCollection', True))
        cursor = None
        try:
            cursor = _db.join(conditions, trans)
            cursor.resolve_shortcuts = resolve_shortcuts
            subfolders = ObjectSet([f for f in cursor])
        finally:
            if cursor != None:
                cursor.close()
        return subfolders
    getSubFolders = deprecated(get_subfolders)
    
    def has_children(self, trans=None):
        """
        Checks if the container has at least one non-container child.
        
        @param trans: A valid transaction handle
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('isCollection', False))
        return _db.test_join(conditions, trans)
    hasChildren = deprecated(has_children)
    
    def has_subfolders(self, trans=None):
        """
        Checks if the container has at least one child container.
        
        @param trans: A valid transaction handle
        @rtype: bool
        """
        conditions = (('_parentid', self._id), ('isCollection', True))
        return _db.test_join(conditions, trans)
    hasSubfolders = deprecated(has_subfolders)

class RecycleBin(Container):
    """
    Recycle bin class.
    
    By default every I{RecycleBin} class instance is a system item.
    It cannot be deleted, copied, moved or recycled.
    """
    __image__ = "desktop/images/trashcan_empty8.gif"
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
        items = self.get_items(trans)
        [item.delete(trans) for item in items]
