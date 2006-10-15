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
"""
This module defines all the custom properties used
by the L{org.innoscript.schemas} module custom objects.
"""

from porcupine.datatypes import *

class file(File):
    """
    Simple file attribute.
    
    Added in:
        1. L{File<org.innoscript.schemas.common.File>}
    """
    __slots__ = ()
    isRequired = True

class launchUrl(String):
    """
    A Url to valid QuiX file.
    
    Added in:
        1. L{Application<org.innoscript.schemas.common.Application>}
    """
    __slots__ = ()
    isRequired = True

class category_objects(RelatorN):
    """
    The objects that a category has.
    
    Added in:
        1. L{Category<org.innoscript.schemas.common.Category>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.schemas.common.Document', 
        'org.innoscript.schemas.collab.Contact', 
    )
    relAttr = 'categories'
    
class categories(RelatorN):
    """
    The categories that an object belongs to.
    
    Added in:
        1. L{Document<org.innoscript.schemas.common.Document>}
        2. L{Contact<org.innoscript.schemas.collab.Contact>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.schemas.common.Category',
    )
    relAttr = 'category_objects'
        
class memberof(RelatorN):
    """
    The groups that a user is member of.
    
    Added in:
        1. L{GenericUser<org.innoscript.schemas.security.GenericUser>}
        2. L{GuestUser<org.innoscript.schemas.security.GuestUser>}
    """
    __slots__ = ()
    relCc = ('org.innoscript.schemas.security.Group', )
    relAttr = 'members'

class password(Password):
    """
    The user's password.
    
    Added in:
        1. L{User<org.innoscript.schemas.security.User>}
    """
    __slots__ = ()
    isRequired = True

class members(RelatorN):
    """
    A group's members.
    
    Added in:
        1. L{Group<org.innoscript.schemas.security.Group>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.schemas.security.User',
        'org.innoscript.schemas.security.GuestUser'
    )
    relAttr = 'memberof'
    
class policies(RelatorN):
    """
    List of policies assigned to an object.
    
    Added in:
        1. L{GuestUser<org.innoscript.schemas.security.GuestUser>}
        2. L{User<org.innoscript.schemas.security.User>}
        3. L{Group<org.innoscript.schemas.security.Group>}
        4. L{EveryoneGroup<org.innoscript.schemas.security.EveryoneGroup>}
        5. L{AuthUsersGroup<org.innoscript.schemas.security.AuthUsersGroup>}
    """
    __slots__ = ()
    relCc = ('org.innoscript.schemas.security.Policy', )
    relAttr = 'policyGranted'

class policyGranted(RelatorN):
    """
    List of objects that a policy is assigned to.
    
    Added in:
        1. L{Policy<org.innoscript.schemas.security.Policy>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.schemas.security.GuestUser',
        'org.innoscript.schemas.security.User',
        'org.innoscript.schemas.security.Group',
        'org.innoscript.schemas.security.EveryoneGroup',
        'org.innoscript.schemas.security.AuthUsersGroup'
    )
    relAttr = 'policies'
