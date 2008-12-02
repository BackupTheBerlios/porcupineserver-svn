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
Porcupine datatypes
===================
Base classes for custom data types.

See also the L{org.innoscript.desktop.schema.properties} module as
a usage guideline.
"""

import copy
import md5
import os.path
import shutil
import cStringIO

from porcupine import db
from porcupine.utils import misc, date
from porcupine.core import objectSet
from porcupine import exceptions
from porcupine.core import dteventhandlers


class DataType(object):
    """
    Base data type class.
    
    Use this as a base class if you want to create your own custom datatype.
    
    @cvar isRequired: boolean indicating if the data type is mandatory
    @type isRequired: bool
    """
    __slots__ = ()
    _eventHandler = None
    isRequired = False

    def validate(self):
        """
        Data type validation method.
        
        This method is called automatically for each I{DataType}
        instance attribute of an object, whenever this object
        is appended or updated.
        
        @raise TypeError:
            if the value is not of the right type.
        @raise ValueError: 
            if the data type is mandatory and is empty.
        
        @return: None
        """
        if not isinstance(self.value, self._safetype):
            raise TypeError, \
               'Invalid data type for "%s". Got "%s" instead of "%s".' % \
               (self.__class__.__name__, self.value.__class__.__name__,
                self._safetype.__name__)
        if self.isRequired and not self.value:
            raise ValueError, \
               '"%s" attribute is mandatory' % self.__class__.__name__

class String(DataType):
    """String data type
    
    @ivar value: The datatype's value
    @type value: str
    """
    __slots__ = ('value', )
    _safetype = str
    
    def __init__(self, **kwargs):
        self.value = ''
        
class RequiredString(String):
    "Mandatory L{String} data type."
    __slots__ = ()
    isRequired = True

class Integer(DataType):
    """Integer data type

    @ivar value: The datatype's value
    @type value: int
    """
    __slots__ = ('value', )
    _safetype = int
    
    def __init__(self, **kwargs):
        self.value = 0
        
class RequiredInteger(Integer):
    "Mandatory L{Integer} data type."
    __slots__ = ()
    isRequired = True

class Float(DataType):
    """Float data type

    @ivar value: The datatype's value
    @type value: float
    """
    __slots__ = ('value', )
    _safetype = float
    
    def __init__(self, **kwargs):
        self.value = 0.0
        
class RequiredFloat(Float):
    "Mandatory L{Float} data type."
    __slots__ = ()
    isRequired = True
        
class Boolean(DataType):
    """Boolean data type
    
    @ivar value: The datatype's value
    @type value: bool
    """
    __slots__ = ('value', )
    _safetype = bool
    
    def __init__(self, **kwargs):
        self.value = False
        
class List(DataType):
    """List data type
    
    @ivar value: The datatype's value
    @type value: list
    """
    __slots__ = ('value', )
    _safetype = list
    
    def __init__(self, **kwargs):
        self.value = []

class RequiredList(List):
    "Mandatory L{List} data type."
    __slots__ = ()
    isRequired = True
   
class Dictionary(DataType):
    """Dictionary data type
    
    @ivar value: The datatype's value
    @type value: dict
    """
    __slots__ = ('value', )
    _safetype = dict
    
    def __init__(self, **kwargs):
        self.value = {}

class RequiredDictionary(Dictionary):
    "Mandatory L{Dictionary} data type."
    __slots__ = ()
    isRequired = True

class Date(DataType, date.Date):
    "Date data type"
    __slots__ = ()
    _safetype = float
    
    def __init__(self, **kwargs):
        date.Date.__init__(self)

class DateTime(Date):
    "Datetime data type"
    __slots__ = ()

class Password(DataType):
    """
    Password data type.
    
    This data type is actually storing MD5 hex digests
    of the assigned string value.

    @ivar value: The datatype's value
    @type value: str
    """
    __slots__ = ('_value', )
    _blank = 'd41d8cd98f00b204e9800998ecf8427e'
    
    def __init__(self, **kwrags):
        self._value = self._blank

    def validate(self):
        assert not self.isRequired or not self._value == self._blank, \
               '"%s" attribute is mandatory' % self.__class__.__name__
    
    def getValue(self):
        return self._value
    
    def setValue(self, sValue):
        if sValue != self._value:
            self._value = md5.new(sValue).hexdigest()
    
    value = property(getValue, setValue)
    
class RequiredPassword(Password):
    "Mandatory L{Password} data type."
    __slots__ = ()
    isRequired = True

class Reference1(DataType):
    """
    This data type is used whenever an item losely references
    at most one other item. Using this data type, the referenced item
    B{IS NOT} aware of the items that reference it.

    @cvar relCc: a list of strings containing all the permitted content
                 classes that the instances of this type can reference.

    @ivar value: The ID of the referenced object
    @type value: str

    """
    __slots__ = ('value', )
    _safetype = str
    relCc = ()
    
    def __init__(self, **kwargs):
        self.value = ''

    def getItem(self, trans=None):
        """
        This method returns the object that this data type
        instance references. If the current user has no read
        permission on the referenced item or it has been deleted
        then it returns None.
        
        @param trans: A valid transaction handle
        
        @rtype: type
        @return: The referenced object, otherwise None
        """
        oItem = None
        if self.value:
            try:
                oItem = db.getItem(self.value, trans)
            except exceptions.ObjectNotFound:
                pass
        return(oItem)

class RequiredReference1(Reference1):
    "Mandatory L{Reference1} data type."
    __slots__ = ()
    isRequired = True

class ReferenceN(DataType):
    """
    This data type is used whenever an item losely references
    none, one or more than one items. Using this data type, the referenced items
    B{ARE NOT} aware of the items that reference them.

    @ivar value: The IDs of the referenced objects
    @type value: list

    @cvar relCc: a list of strings containing all the permitted content
                 classes that the instances of this type can reference.
    """
    __slots__ = ('value', )
    _safetype = list
    relCc = ()

    def __init__(self, **kwargs):
        self.value = []
    
    def getItems(self, trans=None):
        """
        This method returns the items that this data type
        instance references.
        
        @param trans: A valid transaction handle
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        return(objectSet.ObjectSet(self.value, txn=trans,
                                   resolved=False, safe=False))

class RequiredReferenceN(ReferenceN):
    "Mandatory L{ReferenceN} data type."
    __slots__ = ()
    isRequired = True

class Relator1(Reference1):
    """
    This data type is used whenever an item possibly references another item.
    The referenced item B{IS} aware of the items that reference it.
    
    @cvar relAttr: contains the name of the attribute of the referenced
                   content classes. The type of the referenced attribute should
                   be B{strictly} be a subclass of L{Relator1} or L{RelatorN}
                   data types for one-to-one and one-to-many relationships
                   respectively.
    @type relAttr: str

    @cvar respectsReferences: if set to C{True} then the object cannot be
                              deleted if there are objects that reference it.
    @type respectsReferences: bool
    """
    __slots__ = ()
    _eventHandler = dteventhandlers.Relator1EventHandler
    respectsReferences = False
    relAttr = ''
    
class RequiredRelator1(Relator1):
    "Mandatory L{Relator1} data type."
    __slots__ = ()
    isRequired = True

class RelatorN(ReferenceN):
    """
    This data type is used whenever an item references none, one or more items.
    The referenced items B{ARE} aware of the items that reference them.
    
    @cvar relAttr: the name of the attribute of the referenced content classes.
                   The type of the referenced attribute should be B{strictly}
                   be a subclass of L{Relator1} or L{RelatorN} data types for
                   one-to-many and many-to-many relationships respectively.
    @type relAttr: str

    @cvar respectsReferences: if set to C{True} then the object
                              cannot be deleted if there are objects that
                              reference it.
    @type respectsReferences: bool
    """
    __slots__ = ()
    _eventHandler = dteventhandlers.RelatorNEventHandler
    relAttr = ''
    respectsReferences = False
    
class RequiredRelatorN(RelatorN):
    "Mandatory L{RelatorN} data type."
    __slots__ = ()
    isRequired = True

class Composition(DataType):
    """
    This data type is used for embedding composite objects to
    the assigned content type.
    
    @cvar compositeClass: the name of the content class that can be embedded.
    
    @ivar value: list of the embedded objects. Must be instances of
                 L{porcupine.systemObjects.Composite}.
    @type value: list
    
    @see: L{porcupine.systemObjects.Composite}
    """
    __slots__ = ('value', )
    _safetype = list
    _eventHandler = dteventhandlers.CompositionEventHandler
    compositeClass = ''

    def __init__(self, **kwargs):
        self.value = []

    def getItems(self, trans=None):
        """
        Returns the items that this data type instance embeds.
        
        @param trans: A valid transaction handle
        
        @rtype: L{ObjectSet<porcupine.core.objectSet.ObjectSet>}
        """
        return objectSet.ObjectSet(self.value, txn=trans, resolved=True)

class RequiredComposition(Composition):
    "Mandatory L{Composition} data type."
    __slots__ = ()
    isRequired = True

#===============================================================================
# External Attributes
#===============================================================================

class ExternalAttribute(DataType):
    """
    Subclass I{ExternalAttribute} when dealing with large attribute lengths.
    These kind of attributes are not stored on the same database as
    all other object attributes.
    
    @type isDirty: bool
    @type value: str
    """
    __slots__ = ('_id', '_value', '_isDirty')
    _safetype = str
    _eventHandler = dteventhandlers.ExternalAttributeEventHandler
    
    def __init__(self, **kwargs):
        self._id = misc.generateOID()
        self._reset()

    def _reset(self):
        self._value = None
        self._isDirty = False

    def __deepcopy__(self, memo):
        clone = copy.copy(self)
        clone._id = misc.generateOID()
        clone.value = self.getValue()
        return clone

    def getValue(self, txn=None):
        "L{value} property getter"
        if self._value is None:
            #trans = currentThread().trans
            self._value = \
                db._db.db_handle._getExternalAttribute(self._id, txn) \
                or ''
        return(self._value)

    def setValue(self, value):
        "L{value} property setter"
        self._isDirty = True
        self._value = value

    value = property(getValue, setValue, None, "the actual value")

    def getIsDirty(self):
        "L{isDirty} property getter"
        return self._isDirty
    isDirty = property(getIsDirty, None, None,
                       "boolean indicating if the value has changed")

class Text(ExternalAttribute):
    """Data type to use for large text streams
    
    @type value: str
    """
    __slots__ = ('_size', )
    
    def __init__(self, **kwargs):
        ExternalAttribute.__init__(self, **kwargs)
        self._size = 0

    def setValue(self, value):
        ExternalAttribute.setValue(self, value)
        self._size = len(value)

    value = property(ExternalAttribute.getValue, setValue, None, "text stream")

    def __len__(self):
        return(self._size)

    def validate(self):
        assert not self.isRequired or self._size, \
               '"%s" attribute is mandatory' % self.__class__.__name__

class RequiredText(Text):
    "Mandatory L{Text} data type."
    __slots__ = ()
    isRequired = True
        
class File(Text):
    """Data type to use for file objects
    
    @ivar filename: the file's name
    @type filename: str
    """
    __slots__ = ('filename', )
    
    def __init__(self, **kwargs):
        Text.__init__(self, **kwargs)
        self.filename = ''
        
    def getFile(self):
        return cStringIO.StringIO(self.value)
        
    def loadFromFile(self, fname):
        """
        This method sets the value property of this data type instance
        to a stream read from a file that resides on the file system.
        
        @param fname: A valid filename
        @type fname: str
        
        @return: None
        """
        oFile = file(fname, 'rb')
        self.value = oFile.read()
        oFile.close()

class RequiredFile(File):
    "Mandatory L{File} data type."
    __slots__ = ()
    isRequired = True
        
class ExternalFile(String):
    """Datatype for linking external files. Its value
    is a string which contains the path to the file.
    """
    __slots__ = ()
    _eventHandler = dteventhandlers.ExternalFileEventHandler
    removeFileOnDeletion = True
    isRequired = True
    
    def getFile(self, mode='rb'):
        return file(self.value, mode)
    
    def __deepcopy__(self, memo):
        clone = copy.copy(self)
        duplicate_files = memo.get('df', False)
        if (duplicate_files):
            # copy the external file
            fcounter = 1
            old_filename = new_filename = self.value
            filename, extension = os.path.splitext(old_filename)
            filename = filename.split('_')[0]
            while os.path.exists(new_filename):
                new_filename = ('%s_%d%s' % (filename, fcounter, extension))
                fcounter += 1
            shutil.copyfile(old_filename, new_filename)
            clone.value = new_filename
        return clone

class RequiredExternalFile(ExternalFile):
    "Mandatory L{ExternalFile} data type."
    __slots__ = ()
    isRequired = True
