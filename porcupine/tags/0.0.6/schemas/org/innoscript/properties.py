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
by the L{schemas.org.innoscript} module custom objects.
"""

from porcupine.datatypes import *

class file(File):
    """
    Simple file attribute.
    
    Added in:
        1. L{File<schemas.org.innoscript.common.File>}
    """
    __slots__ = ()
    isRequired = True

class icon(String):
    """
    Icon URL.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()

class top(String):
    """
    Y-coordinate in pixels or percentage.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class left(String):
    """
    X-coordinate in pixels or percentage.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class width(String):
    """
    Width in pixels or percentage.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    isRequired = True
    
class height(String):
    """
    Width in pixels or percentage.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    isRequired = True
    
class isResizable(Boolean):
    """
    Boolean declaring if a window is resizable or not.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class canMaximize(Boolean):
    """
    Boolean declaring if a window can be maximized or not.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class canMinimize(Boolean):
    """
    Boolean declaring if a window can be minimized or not.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class interface(Text):
    """
    Large string containing a QuiX interface description.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    isRequired = True
        
class script(Text):
    """
    Large string containing the javascript code for
    for an application startup.
    
    Added in:
        1. L{Application<schemas.org.innoscript.common.Application>}
    """
    __slots__ = ()
    
class category_objects(RelatorN):
    """
    The objects that a category has.
    
    Added in:
        1. L{Category<schemas.org.innoscript.common.Category>}
    """
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.common.Document', 
        'schemas.org.innoscript.collab.Contact', 
    )
    relAttr = 'categories'
    
class categories(RelatorN):
    """
    The categories that an object belongs to.
    
    Added in:
        1. L{Document<schemas.org.innoscript.common.Document>}
        2. L{Contact<schemas.org.innoscript.collab.Contact>}
    """
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.common.Category',
    )
    relAttr = 'category_objects'
        
class fullName(String):
    """
    A person's full name.
    
    Added in:
        1. L{GenericUser<schemas.org.innoscript.security.GenericUser>}
    """
    __slots__ = ()
    
class memberof(RelatorN):
    """
    The groups that a user is member of.
    
    Added in:
        1. L{GenericUser<schemas.org.innoscript.security.GenericUser>}
        2. L{GuestUser<schemas.org.innoscript.security.GuestUser>}
    """
    __slots__ = ()
    relCc = ('schemas.org.innoscript.security.Group', )
    relAttr = 'members'

class password(Password):
    """
    The user's password.
    
    Added in:
        1. L{User<schemas.org.innoscript.security.User>}
    """
    __slots__ = ()
    isRequired = True

class email(String):
    """
    A person's email.
    
    Added in:
        1. L{User<schemas.org.innoscript.security.User>}
        2. L{Contact<schemas.org.innoscript.collab.Contact>}
    """
    __slots__ = ()
    
class company(String):
    """
    A person's company.
    
    Added in:
        1. L{Contact<schemas.org.innoscript.collab.Contact>}
    """
    __slots__ = ()
    
class members(RelatorN):
    """
    A group's members.
    
    Added in:
        1. L{Group<schemas.org.innoscript.security.Group>}
    """
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.security.User',
        'schemas.org.innoscript.security.GuestUser'
    )
    relAttr = 'memberof'
    
class policies(RelatorN):
    """
    List of policies assigned to an object.
    
    Added in:
        1. L{GuestUser<schemas.org.innoscript.security.GuestUser>}
        2. L{User<schemas.org.innoscript.security.User>}
        3. L{Group<schemas.org.innoscript.security.Group>}
        4. L{EveryoneGroup<schemas.org.innoscript.security.EveryoneGroup>}
        5. L{AuthUsersGroup<schemas.org.innoscript.security.AuthUsersGroup>}
    """
    __slots__ = ()
    relCc = ('schemas.org.innoscript.security.Policy', )
    relAttr = 'policyGranted'

class policyGranted(RelatorN):
    """
    List of objects that a policy is assigned to.
    
    Added in:
        1. L{Policy<schemas.org.innoscript.security.Policy>}
    """
    __slots__ = ()
    relCc = (
        'schemas.org.innoscript.security.GuestUser',
        'schemas.org.innoscript.security.User',
        'schemas.org.innoscript.security.Group',
        'schemas.org.innoscript.security.EveryoneGroup',
        'schemas.org.innoscript.security.AuthUsersGroup'
    )
    relAttr = 'policies'
