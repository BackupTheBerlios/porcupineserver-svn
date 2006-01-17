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
"Porcupine common objects"

from porcupine import systemObjects as system
from schemas.org.innoscript import properties
from porcupine import datatypes

class File(system.Item):
    """Simple file object

    @ivar file: The file data type
    @type file: L{file<schemas.org.innoscript.properties.file>}
    """
    __image__ = "images/document.gif"
    __slots__ = ('file',)
    __props__ = system.Item.__props__ + __slots__
    
    def __init__(self):
        system.Item.__init__(self)
        self.file = properties.file()

    def getSize(self):
        "Getter for L{size} property"
        return(len(self.file))
    size = property(getSize, None, None, "The file's size")

class RecycleBin(system.RecycleBin):
    """
    System Recycle Bin
    ==================
    This recycle bin class has no parent container and
    its instance is the target container of all user deletions.
    If you need a recycle bin for each user subclass the
    L{porcupine.systemObjects.RecycleBin}.
    """
    __slots__ = ()
    
    def getParent(self):
        return None

class RootFolder(system.Container):
    """
    Root Folder
    ===========
    This is the root folder, the root container of all
    Porcupine objects.
    """
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.common.Folder',
        'schemas.org.innoscript.collab.ContactsFolder',
    )
    
    def getParent(self):
        return None

class AdminTools(system.Container):
    """
    Administrative Tools Folder
    ===========================
    This folder contains the users, the policies and
    the installed applications containers.
    """
    __image__ = "images/admintools.gif"
    __slots__ = ()
        
class AppsFolder(system.Container):
    """
    Installed Applications Folder
    """
    __image__ = "images/appsfolder.gif"
    __slots__ = ()
    containment = ('schemas.org.innoscript.common.Application',)

class Application(system.Item):
    """B{QuiX} Application Object
    
    @ivar icon: The application's icon url
    @type icon: L{icon<schemas.org.innoscript.properties.icon>}
    
    @ivar width: The application's width
    @type width: L{width<schemas.org.innoscript.properties.width>}

    @ivar height: The application's height
    @type height: L{height<schemas.org.innoscript.properties.height>}

    @ivar top: The application's top coordinate
    @type top: L{top<schemas.org.innoscript.properties.top>}

    @ivar left: The application's left coordinate
    @type left: L{top<schemas.org.innoscript.properties.top>}

    @ivar resourcesImportPath: This is the full import path to a module variable
        of type "L{ResourceStrings<porcupine.config.resources.ResourceStrings>}"
    @type resourcesImportPath: L{String<porcupine.datatypes.String>}

    @ivar isResizable: Indicates if the application's window is resizable
    @type isResizable: L{isResizable<schemas.org.innoscript.properties.isResizable>}

    @ivar canMaximize: Indicates if the application's window is maximizable
    @type canMaximize: L{canMaximize<schemas.org.innoscript.properties.canMaximize>}

    @ivar canMinimize: Indicates if the application's window is minimizable
    @type canMinimize: L{canMinimize<schemas.org.innoscript.properties.canMinimize>}

    @ivar interface: The application's interface in QuiX xml format
    @type interface: L{interface<schemas.org.innoscript.properties.interface>}

    @ivar script: The main script required for the application start up
    @type script: L{script<schemas.org.innoscript.properties.script>}
    """
    __image__ = "images/app.gif"
    __slots__ = (
        'icon','width','height','top','left',
        'isResizable','canMaximize','canMinimize',
        'interface','script','resourcesImportPath'
    )
    __props__ = system.Item.__props__ + __slots__
    
    def __init__(self):
        system.Item.__init__(self)
        self.isResizable = properties.isResizable()
        self.canMinimize = properties.canMinimize()
        self.canMaximize = properties.canMaximize()
        self.icon = properties.icon()
        self.width = properties.width()
        self.height = properties.height()
        self.top = properties.top()
        self.left = properties.left()
        self.interface = properties.interface()
        self.script = properties.script()
        self.resourcesImportPath = datatypes.String()
        
    def getInterface(self, rootURI):
        """
        Adds the required boilerplate to the
        L{interface} property.
        
        @param rootURI: The server root URI including the
            session ID e.g.
            C{http://www.innoscript.org/porcupine.py/{7ee699bd4fcdeba32aef3d10eac3d6f4}}
        @type rootURI: str
        
        @rtype: str
        """
        sTitle = self.displayName.value
        if self.isResizable.value:
            sResizable = 'true'
        else:
            sResizable = 'false'
        if self.canMinimize.value:
            sMinimize = 'true'
        else:
            sMinimize = 'false'
        if self.canMaximize.value:
            sMaximize = 'true'
        else:
            sMaximize = 'false'
        sIcon = self.icon.value
        sWidth = self.width.value.replace('%', '%%')
        sHeight = self.height.value.replace('%', '%%')
        sTop = self.top.value.replace('%', '%%')
        sLeft = self.left.value.replace('%', '%%')
        sInterface = self.interface.value
        sID = self.id
        sIface = '''<?xml version="1.0" encoding="utf-8"?>
        <a:window xmlns:a="http://www.innoscript.org/quix"
            title="%(sTitle)s" resizable="%(sResizable)s" close="true"
            minimize="%(sMinimize)s" maximize="%(sMaximize)s" img="%(sIcon)s"
            width="%(sWidth)s" height="%(sHeight)s" left="%(sLeft)s" top="%(sTop)s">
            <a:script name="%(sTitle)s Script" src="%(rootURI)s/%(sID)s?cmd=getscript"></a:script>
            <a:wbody>%(sInterface)s</a:wbody>
        </a:window>''' % vars()
        return sIface
        
    def getSize(self):
        "Getter of L{size} property"
        return len(self.interface) + len(self.script)
    size = property(getSize, None, None,
                        'The application\'s size in bytes')

class Folder(system.Container):
    """
    Common Folder
    =============
    This type of folder can contain folders and documents.
    """
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.common.Folder',
        'schemas.org.innoscript.common.Document'
    )

class Category(system.Container):
    """Category

    @ivar category_objects: The objects contained in this category
    @type category_objects: L{category_objects<schemas.org.innoscript.properties.
                            category_objects>}
    """
    __image__ = "images/category.gif"
    __slots__ = ('category_objects',)
    __props__ = system.Container.__props__ + __slots__
    containment = ('schemas.org.innoscript.common.Category',)
    
    def __init__(self):
        system.Container.__init__(self)
        self.category_objects = properties.category_objects()

class Document(File):
    """Document with categorization capabilities
    
    @ivar categories: The document's categories
    @type categories: L{categories<schemas.org.innoscript.properties.categories>}
    """
    __slots__ = ('categories',)
    __props__ = File.__props__ + __slots__
    
    def __init__(self):
        File.__init__(self)
        self.categories = properties.categories()
