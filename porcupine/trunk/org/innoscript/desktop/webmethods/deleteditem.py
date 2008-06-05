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
Web methods for the deleted item content class
"""
from porcupine import db
from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filters
from porcupine.utils import date, xml
from porcupine.systemObjects import DeletedItem

from org.innoscript.desktop.webmethods import baseitem

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=DeletedItem, template='../ui.Frm_DeletedItem.quix')
def properties(self):
    "Displays the deleted item's properties form"
    context = HttpContext.current()
    sLang = context.request.getLang()
    modified = date.Date(self.modified)
    return {
        'ICON': self.__image__,
        'NAME': xml.xml_encode(self.originalName),
        'LOC': xml.xml_encode(self.originalLocation),
        'MODIFIED': modified.format(baseitem.DATES_FORMAT, sLang),
        'MODIFIED_BY': xml.xml_encode(self.modifiedBy),
        'CONTENTCLASS': self.getDeletedItem().contentclass
    }
    
@webmethods.remotemethod(of_type=DeletedItem)
@db.transactional()
def restore(self):
    "Restores the deleted item to its orginal location"
    txn = db.getTransaction()
    self.restore(txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=DeletedItem)
@db.transactional()
def restoreTo(self, targetid):
    "Restores the deleted item to the designated target container"
    txn = db.getTransaction()
    self.restoreTo(targetid, txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=DeletedItem)
@db.transactional()
def delete(self):
    "Removes the deleted item"
    txn = db.getTransaction()
    self.delete(txn)
    txn.commit()
    return True
