#===============================================================================
#    Copyright 2005-2007, Tassos Koutsovassilis
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
Web methods for the group content class
"""

from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filter
from porcupine.security import objectAccess
from porcupine.utils import date, xmlUtils

from org.innoscript.desktop.schema.security import Group
from org.innoscript.desktop.webmethods import base

@filter.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=Group, template='../ui.Frm_GroupProperties.quix')
def properties(self):
    "Displays the group's properties form"
    context = HttpContext.current()

    context.response.setHeader('cache-control', 'no-cache')
    sLang = context.request.getLang()

    user = context.session.user
    iUserRole = objectAccess.getAccess(self, user)
    readonly = (iUserRole==1)

    params = {
        'ID' : self.id,
        'ICON' : self.__image__,
        'SELECT_FROM_POLICIES' : 'policies',
        'POLICIES_REL_CC' : '|'.join(self.policies.relCc),
        'NAME' : self.displayName.value,
        'DESCRIPTION' : self.description.value,
        'MODIFIED' : date.Date(self.modified).format(base.DATES_FORMAT, sLang),
        'MODIFIED_BY' : self.modifiedBy,
        'CONTENTCLASS' : self.contentclass,
        'SELECT_FROM' : self.parentid,
        'REL_CC' : '|'.join(self.members.relCc),
        'READONLY' : str(readonly).lower()
    }

    members_options = []
    members = self.members.getItems()
    for user in members:
        members_options += [xmlUtils.XMLEncode(user.__image__),
                            user.id,
                            xmlUtils.XMLEncode(user.displayName.value)]
    params['MEMBERS'] = ';'.join(members_options)

    policies_options = []
    policies = self.policies.getItems()
    for policy in policies:
        policies_options += [xmlUtils.XMLEncode(policy.__image__),
                             policy.id,
                             xmlUtils.XMLEncode(policy.displayName.value)]
    params['POLICIES'] = ';'.join(policies_options)
    
    params['SECURITY_TAB'] = base._getSecurity(self, user)
    
    return params

