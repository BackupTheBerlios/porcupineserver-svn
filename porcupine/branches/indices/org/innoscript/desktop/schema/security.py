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
"Porcupine desktop security objects"

import hashlib

from porcupine import systemObjects as system
from porcupine import datatypes
from org.innoscript.desktop.schema import properties
from org.innoscript.desktop.schema import handlers

class PoliciesFolder(system.Container):
    """
    Server Policies Folder
    ======================
    A container type for all the security policies
    """
    __image__ = "desktop/images/policies.gif"
    containment = ('org.innoscript.desktop.schema.security.Policy',)
    
class Policy(system.Item):
    """
    Server Policy
    =============
    Policy is a way for securing HTTP exposed methods.
    Policies take precedence over security descriptors.
    
    They are extremely usefull, if used on XML-RPC servlets
    which have arbitary methods. Sample usage::
        
        from porcupine.security.policy import policymethod
        from porcupine.core.servlet import XMLRPCServlet
        
        class MyServlet(XMLRPCServlet):
            ...
            def myMethod(self):
                ...
            myMethod = policymethod(myMethod, policyID)
            
    The C{myMethod} method is secured by the policy with ID C{policyID}.
    Only the users and groups that have been granted this policy can
    execute this XML-RPC method.
    
    If a non-authorized user calls C{myMethod} a 
    L{PermissionDenied<porcupine.exceptions.PermissionDenied>}
    exception is raised.

    @ivar policyGranted: The list of users that have been granted this policy.
    @type policyGranted: L{PolicyGranted<org.innoscript.desktop.schema.properties.PolicyGranted>}
    """
    __image__ = "desktop/images/policy.gif"
    __props__ = system.Item.__props__ + ('policyGranted',)
    
    def __init__(self):
        system.Item.__init__(self)
        self.policyGranted = properties.PolicyGranted()

class UsersFolder(system.Container):
    """
    Users Folder
    ============
    This is the container of all users and groups.
    """
    __image__ = "desktop/images/userfolder.gif"
    containment = (
        'org.innoscript.desktop.schema.security.User',
        'org.innoscript.desktop.schema.security.Group'
    )

class GenericUser(system.Item):
    """Generic User object

    @ivar fullName: The user's full name.
    @type fullName: L{String<porcupine.datatypes.String>}

    @ivar memberof: The list of groups that this user belongs to.
    @type memberof: L{MemberOf<org.innoscript.desktop.schema.properties.MemberOf>}

    @ivar policies: The list of policies assigned to this user.
    @type policies: L{Policies<org.innoscript.desktop.schema.properties.Policies>}

    """
    __image__ = "desktop/images/user.gif"
    __props__ = system.Item.__props__ + ('fullName', 'memberof', 'policies')
    
    def __init__(self):
        system.Item.__init__(self)
        self.fullName = datatypes.String()
        self.memberof = properties.MemberOf()
        self.policies = properties.Policies()

    def isMemberOf(self, group):
        """
        Checks if the user is member of the given group.
        
        @param group: the group object
        @type group: L{GenericGroup}
        
        @rtype: bool
        """
        return(group.id in self.memberof.value)

    def isAdmin(self):
        """
        Checks if the user is member of the administrators group.
        
        @rtype: bool
        """
        return('administrators' in self.memberof.value)

class User(GenericUser):
    """Porcupine User object

    @ivar password: The user's password.
    @type password: L{RequiredPassword<porcupine.datatypes.RequiredPassword>}

    @ivar email: The user's email.
    @type email: L{String<porcupine.datatypes.String>}

    @ivar settings: User specific preferences.
    @type settings: L{Dictionary<porcupine.datatypes.Dictionary>}
    """
    __props__ = GenericUser.__props__ + ('password', 'email',
                                         'settings', 'personalFolder')
    _eventHandlers = GenericUser._eventHandlers + [handlers.PersonalFolderHandler]
    
    def __init__(self):
        GenericUser.__init__(self)
        self.password = datatypes.RequiredPassword()
        self.email = datatypes.String()
        self.settings = datatypes.Dictionary()
        self.personalFolder = datatypes.Reference1()

    def authenticate(self, sPsw):
        """Checks if the given string matches the
        user's password.
        
        @param sPsw: The string to check against.
        @type sPsw: str
        
        @rtype: bool
        """
        md = hashlib.md5(sPsw)
        hexDigestP = md.hexdigest()
        return hexDigestP==self.password.value

class SystemUser(system.Item):
    """
    System User
    ===========
    System User is a special user. Its instance is retreived when the
    L{BaseServlet.runAsSystem<porcupine.core.servlet.BaseServlet.runAsSystem>}
    method is called.
    """
    __image__ = "desktop/images/user.gif"
    
    def isAdmin(self):
        """
        System User is an administative account.
        
        @return: C{True}
        """
        return(True)

class GuestUser(GenericUser):
    """
    Guest User
    ==========
    This user instance is assigned by the session manager
    to all new sessions.
    This is configurable. See the C{sessionmanager} section
    of C{porcupine.ini}.
    """

class GenericGroup(system.Item):
    """Generic Group class

    @ivar policies: The list of policies have been asigned to this group.
    @type policies: L{Policies<org.innoscript.desktop.schema.properties.Policies>}
    """
    __props__ = system.Item.__props__ + ('policies', )
    
    def __init__(self):
        system.Item.__init__(self)
        self.policies = properties.Policies()
    
    def hasMember(self, user):
        """
        Not Implemented.
        It must be implemented by subclasses.
        """
        raise NotImplementedError

class Group(GenericGroup):
    """Porcupine Group

    @ivar members: The group's members.
    @type members: L{Members<org.innoscript.desktop.schema.properties.Members>}
    """
    __image__ = "desktop/images/group.gif"
    __props__ = GenericGroup.__props__ + ('members', )
    
    def __init__(self):
        GenericGroup.__init__(self)
        self.members = properties.Members()

    def hasMember(self, user):
        """
        Checks if a user belongs is in this group.
        
        @param user: the user object
        @type user: L{GenericUser}
        
        @rtype: bool
        """
        return(user.id in self.members.value)

class EveryoneGroup(GenericGroup):
    "Everyone Group"
    __image__ = "desktop/images/group.gif"
    
    def hasMember(self, user):
        """
        This method always returns C{True}.
        
        @param user: the user object
        @type user: L{GenericUser}
        
        @return: C{True}
        @rtype: bool
        """
        return(True)

class AuthUsersGroup(GenericGroup):
    "Authenticated Users Group"
    __image__ = "desktop/images/group.gif"
    
    def hasMember(self, user):
        """
        This method returns C{True} only if the user object has
        an attribute named C{password} else it returns C{False}.
        
        @param user: the user object
        @type user: L{GenericUser}
        
        @rtype: bool
        """
        return(hasattr(user, 'password'))