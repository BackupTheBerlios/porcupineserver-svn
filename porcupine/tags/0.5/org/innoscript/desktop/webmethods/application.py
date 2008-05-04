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
Web methods for the application content class
"""

from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filters
from porcupine.security import objectAccess
from porcupine.utils import date, xml

from org.innoscript.desktop.schema.common import Application
from org.innoscript.desktop.webmethods import baseitem

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=Application,
                   template='../ui.Frm_AppProperties.quix')
def properties(self):
    "Displays the application's properties form"
    context = HttpContext.current()
    context.response.setHeader('Cache-Control', 'no-cache')
    sLang = context.request.getLang()
    user = context.session.user
    iUserRole = objectAccess.getAccess(self, user)
    readonly = (iUserRole==1)
    modified = date.Date(self.modified)
    return {
        'ID' : self.id,
        'IMG' : self.__image__,
        'NAME' : self.displayName.value,
        'DESCRIPTION' : self.description.value,
        'ICON' : self.icon.value,
        'LAUNCH_URL' : xml.xml_encode(self.launchUrl.value),
        'MODIFIED' : modified.format(baseitem.DATES_FORMAT, sLang),
        'MODIFIED_BY' : self.modifiedBy,
        'CONTENTCLASS' : self.contentclass,
        'SECURITY_TAB' : baseitem._getSecurity(self, context.session.user),
        'READONLY' : str(readonly).lower()
    }