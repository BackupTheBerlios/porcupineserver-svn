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
Web methods for the users' container class
"""
from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filters

from org.innoscript.desktop.schema import security
from org.innoscript.desktop.webmethods import baseitem

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=security.UsersFolder,
                   qs="cc=org.innoscript.desktop.schema.security.User",
                   template='../ui.Frm_UserNew.quix',
                   max_age=1200)
def new(self):
    "Displays the form for creating a new user"
    context = HttpContext.current()
    oUser = security.User()
    return {
        'CC' : oUser.contentclass,
        'URI' : self.id,
        'REL_CC' : '|'.join(oUser.memberof.relCc),
        'ICON' : oUser.__image__,
        'SELECT_FROM_POLICIES' : 'policies',
        'POLICIES_REL_CC' : '|'.join(oUser.policies.relCc),
        'SECURITY_TAB' : baseitem._getSecurity(self, context.user, True)
    }

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=security.UsersFolder,
                   qs="cc=org.innoscript.desktop.schema.security.Group",
                   template='../ui.Frm_GroupNew.quix',
                   max_age=1200)
def new(self):
    context = HttpContext.current()
    oGroup = security.Group()
    return {
        'CC' : oGroup.contentclass,
        'URI' : self.id,
        'REL_CC' : '|'.join(oGroup.members.relCc),
        'ICON' : oGroup.__image__,
        'SELECT_FROM_POLICIES' : 'policies',
        'POLICIES_REL_CC' : '|'.join(oGroup.policies.relCc),
        'SECURITY_TAB' : baseitem._getSecurity(self, context.user, True)
    }
    
