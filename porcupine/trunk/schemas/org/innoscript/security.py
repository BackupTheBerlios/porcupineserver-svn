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
"Porcupine security objects"

import md5

from porcupine import systemObjects as system
from schemas.org.innoscript import properties
from porcupine import datatypes

class PoliciesFolder(system.Container):
    """
    Server Policies Folder
    ======================
    This container contains all the security policies
    """
    __image__ = "images/policies.gif"
    __slots__ = ()
    containment = ('schemas.org.innoscript.security.Policy',)
    
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
    L{PolicyViolation<porcupine.serverExceptions.PolicyViolation>}
    exception is raised.

    @ivar policyGranted: The list of users that have been granted this policy.
    @type policyGranted: L{policyGranted<schemas.org.innoscript.properties.policyGranted>}
    """
    __image__ = "images/policy.gif"
    __slots__ = ('policyGranted', )
    __props__ = system.Item.__props__ + __slots__
    
    def __init__(self):
        system.Item.__init__(self)
        self.policyGranted = properties.policyGranted()

class UsersFolder(system.Container):
    """
    Users Folder
    ============
    This is the container of all users and groups.
    """
    __image__ = "images/userfolder.gif"
    __slots__ = ()
    containment = (
        'schemas.org.innoscript.security.User',
        'schemas.org.innoscript.security.Group'
    )

class GenericUser(system.Item):
    """Generic User object

    @ivar fullName: The user's full name.
    @type fullName: L{fullName<schemas.org.innoscript.properties.fullName>}

    @ivar memberof: The list of groups that this user belongs to.
    @type memberof: L{memberof<schemas.org.innoscript.properties.memberof>}

    @ivar policies: The list of policies assigned to this user.
    @type policies: L{policies<schemas.org.innoscript.properties.policies>}

    """
    __image__ = "images/user.gif"
    __slots__ = ('fullName', 'memberof', 'policies')
    __props__ = system.Item.__props__ + __slots__
    
    def __init__(self):
        system.Item.__init__(self)
        self.fullName = properties.fullName()
        self.memberof = properties.memberof()
        self.policies = properties.policies()

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
    @type password: L{password<schemas.org.innoscript.properties.password>}

    @ivar email: The user's email.
    @type email: L{email<schemas.org.innoscript.properties.email>}
    """
    __slots__ = ('password', 'email', 'settings')
    __props__ = GenericUser.__props__ + __slots__
    
    def __init__(self):
        GenericUser.__init__(self)
        self.password = properties.password()
        self.email = properties.email()
        self.settings = datatypes.Dictionary()

    def authenticate(self, sPsw):
        """Checks if the given string matches the
        user's password.
        
        @param sPsw: The string to check against.
        @type sPsw: str
        
        @rtype: bool
        """
        md = md5.new(sPsw)
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
    __image__ = "images/user.gif"
    __slots__ = ()
    
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
    __slots__ = ()

class GenericGroup(system.Item):
    """Generic Group class

    @ivar policies: The list of policies have been asigned to this group.
    @type policies: L{policies<schemas.org.innoscript.properties.policies>}
    """
    __slots__ = ('policies', )
    __props__ = system.Item.__props__ + __slots__
    
    def __init__(self):
        system.Item.__init__(self)
        self.policies = properties.policies()
    
    def hasMember(self, user):
        """
        Not Implemented.
        It must be implemented by subclasses.
        """
        raise NotImplementedError

class Group(GenericGroup):
    """Porcupine Group

    @ivar members: The group's members.
    @type members: L{members<schemas.org.innoscript.properties.members>}
    """
    __image__ = "images/group.gif"
    __slots__ = ('members', )
    __props__ = GenericGroup.__props__ + __slots__
    
    def __init__(self):
        GenericGroup.__init__(self)
        self.members = properties.members()

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
    __image__ = "images/group.gif"
    __slots__ = ()
    
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
    __image__ = "images/group.gif"
    __slots__ = ()
    
    def hasMember(self, user):
        """
        This method returns C{True} only if the user has the
        L{password<schemas.org.innoscript.properties.password>}
        attribute else it returns C{False}.
        
        @param user: the user object
        @type user: L{GenericUser}
        
        @rtype: bool
        """
        return(hasattr(user, 'password'))