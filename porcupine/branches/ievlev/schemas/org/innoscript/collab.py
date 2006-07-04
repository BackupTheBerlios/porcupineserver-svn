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
"Porcupine collaboration objects"

from porcupine import systemObjects as system
from schemas.org.innoscript import properties

class ContactsFolder(system.Container):
    "Contacts Folder"
    __image__ = "images/contact_folder.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.collab.ContactsFolder',
        'schemas.org.innoscript.collab.Contact',
    )

class Contact(system.Item):
    """Contact object
    
    @ivar company: The contact's company
    @type company: L{company<schemas.org.innoscript.properties.company>}
    
    @ivar email: The contact's email address
    @type email: L{email<schemas.org.innoscript.properties.email>}
    
    @ivar categories: The contact's categories
    @type categories: L{categories<schemas.org.innoscript.properties.categories>}
    """
    __image__ = "images/contact.gif"
    __slots__ = ('company', 'email', 'categories')
    __props__ = system.Item.__props__ + __slots__
    def __init__(self):
        system.Item.__init__(self)
        self.company = properties.company()
        self.email = properties.email()
        self.categories = properties.categories()
