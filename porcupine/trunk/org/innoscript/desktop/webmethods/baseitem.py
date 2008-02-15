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
Porcupine Desktop web methods for base item content types
=========================================================

Generic interfaces applying to all content classes
unless overriden.
"""
import os

from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filter
from porcupine import datatypes

from porcupine.systemObjects import Item
from porcupine.systemObjects import GenericItem
from porcupine.security import objectAccess
from porcupine.utils import date, xml

from org.innoscript.desktop.strings import resources

AUTO_CONTROLS = {
    datatypes.String: '''
        <rect height="24">
            <label width="100" height="20" caption="%s:"/>
            <field name="%s" left="105"
                width="this.parent.getWidth()-105" value="%s" readonly="%s"/>
        </rect>
        ''',

    datatypes.Boolean: '''
        <rect height="24">
            <label width="100" height="20" caption="%s:"/>
            <field type="checkbox" name="%s" left="105" value="%s"
                readonly="%s"/>
        </rect>
        ''',

    datatypes.File: '''
        <rect height="24">
            <label width="100" height="20" caption="%s:"/>
            <file name="%s" filename="%s" size="%d" href="%s" left="105"
                readonly="%s"/>
        </rect>
        ''',

    datatypes.Text: '''
        <tab caption="%s">
                <field type="textarea" name="%s" width="100%%" height="100%%"
                readonly="%s">%s</field>
        </tab>
        ''',

    datatypes.Date: '''
        <rect height="24">
            <label top="%d" width="100" height="20" caption="%s:"/>
            <datepicker name="%s" left="105" top="%d" width="140" value="%s"
                readonly="%s"/>
        </rect>
        ''',
        
    datatypes.Reference1: '''
        <rect height="24">
            <custom classname="Reference1" width="100%%"
                root="" cc="%s" caption="%s" name="%s" value="%s" dn="%s"
                disabled="%s"/>
        </rect>
        ''',
        
    datatypes.ReferenceN: '''
        <tab caption="%s">
            <custom classname="ReferenceN" width="100%%" height="100%%"
                    root="" cc="%s" name="%s" disabled="%s" value="%s"/>
        </tab>
        '''
}

SECURITY_TAB = '''
<tab caption="@@SECURITY@@" onactivate="generic.getSecurity">
    <custom classname="ACLEditor" width="100%%" height="100%%" rolesinherited="%s"/>
</tab>
'''

DATES_FORMAT = 'ddd, dd month yyyy h12:min:sec MM'

def _getSecurity(forItem, user, rolesInherited=None):
    # get user role
    iUserRole = objectAccess.getAccess(forItem, user)
    if iUserRole == objectAccess.COORDINATOR:
        rolesInherited = rolesInherited or forItem.inheritRoles
        return SECURITY_TAB % str(rolesInherited).lower()
    else:
        return ''
    
def _getControlFromAttribute(item, attrname, attr, readonly, isNew=False):
    attrlabel = '@@%s@@' % attrname
    sControl = ''
    sTab = ''
    
    if isinstance(attr, datatypes.String):
        sControl = AUTO_CONTROLS[datatypes.String] % \
            (attrlabel, attrname,
             attr.value, str(readonly).lower())

    elif isinstance(attr, datatypes.Boolean):
        sControl = AUTO_CONTROLS[datatypes.Boolean] % \
            (attrlabel, attrname,
             str(attr.value).lower(),
             str(readonly).lower())
        
    elif isinstance(attr, datatypes.Date):
        sControl = AUTO_CONTROLS[datatypes.Date] % \
            (attrlabel, attrname,
             attr.toIso8601(), str(readonly).lower())
        
    elif isinstance(attr, datatypes.File):
        if isNew:
            href = ''
        else:
            href = item.id + '?cmd=getfile'
        sControl = AUTO_CONTROLS[datatypes.File] % (
            attrlabel, attrname,
            attr.filename, len(attr), href,
            str(readonly).lower()
        )
        
    elif isinstance(attr, datatypes.Text):
        sTab = AUTO_CONTROLS[datatypes.Text] % (
            attrlabel, attrname, str(readonly).lower(),
            xml.xml_encode(attr.value)
        )
        
    elif isinstance(attr, datatypes.Reference1):
        oRefItem = attr.getItem()
        if oRefItem:
            refid = oRefItem.id
            refname = oRefItem.displayName.value
        else:
            refid = refname = ''
        sReadonly = str(readonly).lower()
        sControl = AUTO_CONTROLS[datatypes.Reference1] % (
            '|'.join(attr.relCc),
            attrlabel,
            attrname,
            refid,
            refname,
            sReadonly
        )
        
    elif isinstance(attr, datatypes.ReferenceN):
        options = []
        rel_items = attr.getItems()
        for item in rel_items:
            options += [xml.xml_encode(item.__image__),
                        item.id,
                        xml.xml_encode(item.displayName.value)]
        
        sTab = AUTO_CONTROLS[datatypes.ReferenceN] % (
            attrlabel,
            '|'.join(attr.relCc),
            attrname,
            str(readonly).lower(),
            ';'.join(options)
        )
    
    return (sControl, sTab)

@filter.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=Item, template='../ui.Frm_AutoProperties.quix')
def properties(self):
    "Displays a generic edit form based on the object's schema"
    context = HttpContext.current()
    
    context.response.setHeader('Cache-Control', 'no-cache')
    sLang = context.request.getLang()
    
    user = context.session.user
    iUserRole = objectAccess.getAccess(self, user)
    readonly = (iUserRole==1)
    modified = date.Date(self.modified)
    
    params = {
        'ID': self.id,
        'ICON': self.__image__,
        'NAME': self.displayName.value,
        'MODIFIED': modified.format(DATES_FORMAT, sLang),
        'MODIFIED_BY': self.modifiedBy,
        'CONTENTCLASS': self.contentclass,
        'PROPERTIES_TAB': '',
        'EXTRA_TABS': '',
        'SECURITY_TAB': _getSecurity(self, context.session.user),
        'UPDATE_DISABLED': str(readonly).lower()
    }
    # inspect item properties
    sProperties = ''
    for attr_name in self.__props__:
        attr = getattr(self, attr_name)
        if isinstance(attr, datatypes.DataType):
            control, tab = \
                _getControlFromAttribute(self, attr_name, attr, readonly)
            sProperties += control
            params['EXTRA_TABS'] += tab
    
    params['PROPERTIES'] = sProperties
        
    return params

@filter.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=Item, template='../ui.Dlg_Rename.quix')
def rename(self):
    "Displays the rename dialog"
    context = HttpContext.current()
    context.response.setHeader('cache-control', 'no-cache')
    return {
        'TITLE': self.displayName.value,
        'ID': self.id,
        'DN': self.displayName.value,
    }

@filter.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=GenericItem, template='../ui.Dlg_SelectContainer.quix') 
def selectcontainer(self):
    "Displays a dialog for selecting the destination container"
    context = HttpContext.current()
    rootFolder = context.server.store.getItem('')
    params = {
        'ROOT_ID': '/',
        'ROOT_IMG': rootFolder.__image__,
        'ROOT_DN': rootFolder.displayName.value,
        'ID': self.id,
    }
    sAction = context.request.queryString['action'][0]
    params['TITLE'] = '@@%s@@' % sAction.upper()
    if sAction != 'select_folder':
        params['TITLE'] += ' &quot;%s&quot;' % self.displayName.value
    return params


@webmethods.remotemethod(of_type=Item)
def update(self, data):
    "Updates an object based on values contained inside the data dictionary"
    context = HttpContext.current()
    # get user role
    iUserRole = objectAccess.getAccess(self, context.session.user)
    if data.has_key('__rolesinherited') and iUserRole == objectAccess.COORDINATOR:
        self.inheritRoles = data.pop('__rolesinherited')
        if not self.inheritRoles:
            acl = data.pop('__acl')
            if acl:
                security = {}
                for descriptor in acl:
                    security[descriptor['id']] = int(descriptor['role'])
                self.security = security

    for prop in data:
        oAttr = getattr(self, prop)
        if isinstance(oAttr, datatypes.File):
            # see if the user has uploaded a new file
            if data[prop]['tempfile']:
                oAttr.filename = data[prop]['filename']
                sPath = self.server.temp_folder + '/' + data[prop]['tempfile']
                oAttr.loadFromFile(sPath)
                os.remove(sPath)
        else:
            oAttr.value = data[prop]
    txn = context.server.store.getTransaction()
    self.update(txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=Item)
def rename(self, newName):
    "Changes the display name of an object"
    context = HttpContext.current()
    txn = context.server.store.getTransaction()
    self.displayName.value = newName
    self.update(txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=Item)
def getSecurity(self):
    "Returns information about the object's security descriptor"
    context = HttpContext.current()
    l = []
    store = context.server.store
    for sID in self.security:
        oUser = store.getItem(sID)
        l.append(
            {
                'id': sID,
                'displayName': oUser.displayName.value,
                'role': str(self.security[sID])
            }
        )
    return(l)

@webmethods.remotemethod(of_type=Item)
def copyTo(self, targetid):
    txn = HttpContext.current().server.store.getTransaction()
    self.copyTo(targetid, txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=Item)
def moveTo(self, targetid):
    txn = HttpContext.current().server.store.getTransaction()
    self.moveTo(targetid, txn)
    txn.commit()
    return True

@webmethods.remotemethod(of_type=Item)
def delete(self):
    txn = HttpContext.current().server.store.getTransaction()
    self.recycle('rb', txn)
    txn.commit()
    return True
