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
"Module for resolving object permissions"

# 1 - read
# 2 - update, delete if owner
# 4 - update, delete anyway
# 8 - full control
NO_ACCESS = 0
READER = 1
AUTHOR = 2
CONTENT_CO = 4
COORDINATOR = 8

def getAccess(oItem, oUser):
    memberOf = ['everyone']
    userID = oUser._id
    if oUser.isAdmin():
        return COORDINATOR
    memberOf.extend(oUser.memberof.value)
    if hasattr(oUser, 'authenticate'):
        memberOf.extend(['authusers']) 
    try:
        iPerm = oItem.security[userID]
        # user explicitly set on ACL
        return iPerm
    except KeyError:
        pass
    lstPerms = [oItem.security.get(groupID, 0) for groupID in memberOf] or [0]
    return(max(lstPerms))
