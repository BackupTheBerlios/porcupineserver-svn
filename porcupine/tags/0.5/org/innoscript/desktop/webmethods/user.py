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
"""
Web methods for the user content class
"""
from porcupine import db
from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filters
from porcupine.security import objectAccess
from porcupine.utils import date, xml

from org.innoscript.desktop.schema.security import User
from org.innoscript.desktop.webmethods import baseitem

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=User,
                   template='../ui.Frm_UserProperties.quix')
def properties(self):
    "Displays the user's properties form"
    context = HttpContext.current()

    context.response.setHeader('cache-control', 'no-cache')
    sLang = context.request.getLang()

    user = context.session.user
    iUserRole = objectAccess.getAccess(self, user)
    readonly = (iUserRole==1)
    params = {
        'ID' : self.id,
        'ICON' : self.__image__,
        'NAME' : self.displayName.value,
        'FULL_NAME' : self.fullName.value,
        'EMAIL' : self.email.value,
        'DESCRIPTION' : self.description.value,
        'MODIFIED' : date.Date(self.modified).format(baseitem.DATES_FORMAT, sLang),
        'MODIFIED_BY' : self.modifiedBy,
        'CONTENTCLASS' : self.contentclass,
        'SELECT_FROM' : self.parentid,
        'REL_CC' : '|'.join(self.memberof.relCc),
        'SELECT_FROM_POLICIES' : 'policies',
        'POLICIES_REL_CC' : '|'.join(self.policies.relCc),
        'READONLY' : str(readonly).lower()
    }
    
    memberof_options = []
    memberof = self.memberof.getItems()
    for group in memberof:
        memberof_options += [xml.xml_encode(group.__image__),
                             group.id,
                             xml.xml_encode(group.displayName.value)]
    params['MEMBEROF'] = ';'.join(memberof_options)
    
    policies_options = []
    policies = self.policies.getItems()
    for policy in policies:
        policies_options += [xml.xml_encode(policy.__image__),
                             policy.id,
                             xml.xml_encode(policy.displayName.value)]
    params['POLICIES'] = ';'.join(policies_options)
    
    params['SECURITY_TAB'] = baseitem._getSecurity(self, user)
    return params

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=User,
                   template='../ui.Frm_UserResetPassword.quix')
def resetpsw(self):
    "Displays the reset password dialog"
    return {
        'URI': self.id,
        'TITLE': self.displayName.value
    }
    
@webmethods.remotemethod(of_type=User)
def resetPassword(self, new_password):
    "Resets the user's password"
    txn = db.getTransaction()
    self.password.value = new_password
    self.update(txn)
    txn.commit()
    return True
