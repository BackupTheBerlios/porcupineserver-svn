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
by the L{org.innoscript.desktop.schema} module custom objects.
"""

from porcupine.datatypes import *

class RequiredFile(File):
    """
    Simple file attribute.
    
    Added in:
        1. L{File<org.innoscript.desktop.schema.common.File>}
    """
    __slots__ = ()
    isRequired = True

class LaunchUrl(String):
    """
    A Url to valid QuiX file.
    
    Added in:
        1. L{Application<org.innoscript.desktop.schema.common.Application>}
    """
    __slots__ = ()
    isRequired = True

class CategoryObjects(RelatorN):
    """
    The objects that a category has.
    
    Added in:
        1. L{Category<org.innoscript.desktop.schema.common.Category>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.desktop.schema.common.Document', 
        'org.innoscript.desktop.schema.collab.Contact', 
    )
    relAttr = 'categories'
    
class Categories(RelatorN):
    """
    The categories that an object belongs to.
    
    Added in:
        1. L{Document<org.innoscript.desktop.schema.common.Document>}
        2. L{Contact<org.innoscript.desktop.schema.collab.Contact>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.desktop.schema.common.Category',
    )
    relAttr = 'category_objects'
        
class MemberOf(RelatorN):
    """
    The groups that a user is member of.
    
    Added in:
        1. L{GenericUser<org.innoscript.desktop.schema.security.GenericUser>}
    """
    __slots__ = ()
    relCc = ('org.innoscript.desktop.schema.security.Group', )
    relAttr = 'members'

class RequiredPassword(Password):
    """
    The user's password.
    
    Added in:
        1. L{User<org.innoscript.desktop.schema.security.User>}
    """
    __slots__ = ()
    isRequired = True

class Members(RelatorN):
    """
    A group's members.
    
    Added in:
        1. L{Group<org.innoscript.desktop.schema.security.Group>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.desktop.schema.security.User',
        'org.innoscript.desktop.schema.security.GuestUser'
    )
    relAttr = 'memberof'
    
class Policies(RelatorN):
    """
    List of policies assigned to an object.
    
    Added in:
        1. L{GuestUser<org.innoscript.desktop.schema.security.GenericUser>}
        2. L{Group<org.innoscript.desktop.schema.security.GenericGroup>}
    """
    __slots__ = ()
    relCc = ('org.innoscript.desktop.schema.security.Policy', )
    relAttr = 'policyGranted'

class PolicyGranted(RelatorN):
    """
    List of objects that a policy is assigned to.
    
    Added in:
        1. L{Policy<org.innoscript.desktop.schema.security.Policy>}
    """
    __slots__ = ()
    relCc = (
        'org.innoscript.desktop.schema.security.GuestUser',
        'org.innoscript.desktop.schema.security.User',
        'org.innoscript.desktop.schema.security.Group',
        'org.innoscript.desktop.schema.security.EveryoneGroup',
        'org.innoscript.desktop.schema.security.AuthUsersGroup'
    )
    relAttr = 'policies'
