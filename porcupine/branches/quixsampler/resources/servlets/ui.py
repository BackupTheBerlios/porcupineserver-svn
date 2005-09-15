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
"QuiX UIs"

from porcupine.core.servlet import XULServlet, HTTPServlet
from porcupine.oql.command import OqlCommand
from porcupine.security import objectAccess
from schemas.org.innoscript import common, security
from porcupine.utils import date, xmlUtils, misc
from porcupine import datatypes

AUTO_CONTROLS = {
    datatypes.String:
        '<a:label top="%d" width="100" height="20" caption="%s:"></a:label>' +
        '<a:field name="%s" left="105" top="%d" width="this.parent.getWidth()-105" value="%s" readonly="%s"></a:field>',

    datatypes.Boolean:
        '<a:label top="%d" width="100" height="20" caption="%s:"></a:label>' +
        '<a:field type="checkbox" name="%s" left="105" top="%d" value="%s" readonly="%s"></a:field>',

    datatypes.File:
        '<a:label top="%d" width="100" height="20" caption="%s:"></a:label>' +
        '<a:file name="%s" filename="%s" size="%d" href="%s" left="105" top="%d" readonly="%s"></a:file>',

    datatypes.Text:
        '<a:tab caption="%s"><a:field type="textarea" name="%s" width="100%%" height="100%%" readonly="%s">%s</a:field></a:tab>',

    datatypes.Date:
        '<a:label top="%d" width="100" height="20" caption="%s:"></a:label>' +
        '<a:datepicker name="%s" left="105" top="%d" width="140" value="%s" readonly="%s"></a:datepicker>',
        
    datatypes.Reference1:
        '<a:rect top="%d" width="100%%" height="24">' +
            '<a:prop name="SelectFrom" value="%s"></a:prop>' +
            '<a:prop name="RelatedCC" value="%s"></a:prop>' +
            '<a:label top="center" width="100" height="20" caption="%s:"></a:label>' +
            '<a:field name="%s" type="hidden" value="%s"></a:field>' +
            '<a:field left="105" top="center" width="this.parent.getWidth()-145" value="%s" readonly="true"></a:field>' +
            '<a:button left="this.parent.getWidth()-40" top="center" caption="..." width="20" height="20" disabled="%s" onclick="generic.selectItem"></a:button>' +
            '<a:button left="this.parent.getWidth()-20" top="center" img="images/cancel8.gif" width="20" height="20" disabled="%s" onclick="generic.clearReference1"></a:button>' +
        '</a:rect>',

    datatypes.ReferenceN: '''
        <a:tab caption="%s">
            <a:splitter width="100%%" height="100%%" orientation="h">
                <a:pane length="-1">
                    <a:selectlist name="%s" multiple="true" posts="all" width="100%%" height="100%%">
                        <a:prop name="SelectFrom" value="%s"></a:prop>
                        <a:prop name="RelatedCC" value="%s"></a:prop>
                        %s
                    </a:selectlist>
                </a:pane>
                <a:pane length="24" disabled="%s">
                    <a:flatbutton width="70" height="22" caption="%s..." onclick="generic.selectItems"></a:flatbutton>
                    <a:flatbutton left="80" width="70" height="22" caption="%s" onclick="generic.removeSelectedItems"></a:flatbutton>
                </a:pane>
            </a:splitter>
        </a:tab>
        '''
}

SECURITY_TAB = '''
<a:tab caption="%s" onactivate="generic.getSecurity">
    <a:splitter orientation="h" spacing="0" width="100%%" height="100%%">
        <a:pane length="24">
            <a:field id="__rolesinherited" name="__rolesinherited" type="checkbox" value="%s" onclick="generic.rolesInherited_onclick"></a:field>
            <a:label left="24" caption="%s"></a:label>
        </a:pane>
        <a:pane length="-1" disabled="%s">
            <a:splitter orientation="v" spacing="0" width="100%%" height="100%%">
                <a:pane length="-1">
                    <a:datagrid id="__acl" name="__acl" width="100%%" height="100%%">
                        <a:listheader>
                            <a:column width="140" caption="%s" name="displayName" editable="false" sortable="true"></a:column>
                            <a:column width="140" caption="%s" name="role" type="optionlist" sortable="true">
                                <a:option value="1" caption="%s"></a:option>
                                <a:option value="2" caption="%s"></a:option>
                                <a:option value="4" caption="%s"></a:option>
                                <a:option value="8" caption="%s"></a:option>
                            </a:column>
                        </a:listheader>
                    </a:datagrid>
                </a:pane>
                <a:pane length="60">
                    <a:flatbutton left="center" width="56" height="22" caption="%s" onclick="generic.addACLEntry"></a:flatbutton>
                    <a:flatbutton top="24" left="center" width="56" height="22" caption="%s" onclick="generic.removeACLEntry"></a:flatbutton>
                </a:pane>
            </a:splitter>
        </a:pane>
    </a:splitter>
</a:tab>
'''

DATES_FORMAT = 'ddd, dd month yyyy h12:min:sec MM'

#================================================================================
# Generic functions
#================================================================================
class PorcupineDesktopServlet(XULServlet):        
    def getSecurity(self, forItem, rolesInherited=None):
        sLang = self.request.getLang()
        user = self.session.user
        # get user role
        iUserRole = objectAccess.getAccess(forItem, user)
        if iUserRole == objectAccess.COORDINATOR:
            rolesInherited = rolesInherited or forItem.inheritRoles
            if rolesInherited:
                sChecked = 'true'
            else:
                sChecked = 'false'
            return SECURITY_TAB % (
                self.server.resources.getResource('SECURITY', sLang),
                sChecked,
                self.server.resources.getResource('ROLES_INHERITED', sLang),
                sChecked,
                self.server.resources.getResource('NAME', sLang),
                self.server.resources.getResource('ROLE', sLang),
                self.server.resources.getResource('ROLE_1', sLang),
                self.server.resources.getResource('ROLE_2', sLang),
                self.server.resources.getResource('ROLE_4', sLang),
                self.server.resources.getResource('ROLE_8', sLang),
                self.server.resources.getResource('ADD', sLang),
                self.server.resources.getResource('REMOVE', sLang)
            )
        else:
            return ''
            
    def getStringFromBoolean(self, bVal):
        if bVal:
            return('true')
        else:
            return('false')

class Frm_Auto(PorcupineDesktopServlet):
    def __init__(self, server, session, request):
        self.yoffset = 0
        PorcupineDesktopServlet.__init__(self, server, session, request)
        
    def getControlFromAttribute(self, attrname, attr, readonly, isNew=False):
        sLang = self.request.getLang()
        attrlabel = self.server.resources.getResource(attrname, sLang)
        sControl = ''
        sTab = ''
        if isinstance(attr, datatypes.String):
            sControl = AUTO_CONTROLS[datatypes.String] % (self.yoffset + 3, attrlabel, attrname, self.yoffset, attr.value, self.getStringFromBoolean(readonly))
            self.yoffset += 25

        elif isinstance(attr, datatypes.Boolean):
            sControl = AUTO_CONTROLS[datatypes.Boolean] % (self.yoffset + 3, attrlabel, attrname, self.yoffset, self.getStringFromBoolean(attr.value), self.getStringFromBoolean(readonly))
            self.yoffset += 25
            
        elif isinstance(attr, datatypes.Date):
            sControl = AUTO_CONTROLS[datatypes.Date] % (self.yoffset + 3, attrlabel, attrname, self.yoffset, attr.toIso8601(), self.getStringFromBoolean(readonly))
            self.yoffset += 25
            
        elif isinstance(attr, datatypes.File):
            if isNew:
                href = ''
            else:
                href = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id + '?cmd=getfile'
            sControl = AUTO_CONTROLS[datatypes.File] % (
                self.yoffset + 3, attrlabel, attrname,
                attr.filename, len(attr), href,
                self.yoffset, self.getStringFromBoolean(readonly)
            )
            self.yoffset += 21
            
        elif isinstance(attr, datatypes.Text):
            sTab = AUTO_CONTROLS[datatypes.Text] % (
                attrlabel, attrname, self.getStringFromBoolean(readonly),
                xmlUtils.XMLEncode(attr.value)
            )
            
        elif isinstance(attr, datatypes.Reference1):
            oRefItem = attr.getItem()
            if oRefItem:
                refid = oRefItem.id
                refname = oRefItem.displayName.value
            else:
                refid = refname = ''
            sReadonly = self.getStringFromBoolean(readonly)
            sControl = AUTO_CONTROLS[datatypes.Reference1] % (
                self.yoffset, self.request.serverVariables['SCRIPT_NAME'] + '/',
                '|'.join(attr.relCc), attrlabel, attrname,
                refid, refname, sReadonly, sReadonly
            )
            self.yoffset += 25
            
        elif isinstance(attr, datatypes.ReferenceN):
            options = ''
            rel_items = attr.getItems()
            for item in rel_items:
                options += '<a:option img="%s" value="%s" ondblclick="autoform.displayRelated" caption="%s"></a:option>' % (item.__image__, item.id, item.displayName.value)
            
            sTab = AUTO_CONTROLS[datatypes.ReferenceN] % (
                attrlabel, attrname,
                self.request.serverVariables['SCRIPT_NAME'] + '/',
                '|'.join(attr.relCc), options, self.getStringFromBoolean(readonly),
                self.server.resources.getResource('ADD', sLang),
                self.server.resources.getResource('REMOVE', sLang)
            )
        
        return (sControl, sTab)

#================================================================================
# Generic item interfaces
#================================================================================

class Frm_AutoProperties(Frm_Auto):
    def setParams(self):
        self.response.setHeader('Cache-Control', 'no-cache')
        sLang = self.request.getLang()
        
        user = self.session.user
        iUserRole = objectAccess.getAccess(self.item, user)
        readonly = (iUserRole==1)
        self.params = {
            'UPDATE': self.server.resources.getResource('UPDATE', sLang),
            'CLOSE': self.server.resources.getResource('CLOSE', sLang),
            'INFO': self.server.resources.getResource('INFO', sLang),
            'DATEMOD': self.server.resources.getResource('DATEMOD', sLang),
            'OBJID': self.server.resources.getResource('ID', sLang),
            'CLASS': self.server.resources.getResource('CLASS', sLang),
            'MODIFIEDBY': self.server.resources.getResource('MODIFIEDBY', sLang),
            
            'ID': self.item.id,
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'ICON': self.item.__image__,
            'NAME': self.item.displayName.value,
            'MODIFIED': date.Date(self.item.modified).format(DATES_FORMAT, sLang),
            'MODIFIED_BY': self.item.modifiedBy,
            'CONTENTCLASS': self.item.contentclass,
            'PROPERTIES_TAB': '',
            'EXTRA_TABS': '',
            'SECURITY_TAB': self.getSecurity(self.item),
            'UPDATE_DISABLED': self.getStringFromBoolean(readonly)    
        }
        # inspect item properties
        sProperties = ''
        for attr_name in self.item.__props__:
            attr = getattr(self.item, attr_name)
            if isinstance(attr, datatypes.DataType):
                control, tab = self.getControlFromAttribute(attr_name, attr, readonly)
                sProperties += control
                self.params['EXTRA_TABS'] += tab
        
        self.params['PROPERTIES_TAB'] = '<a:tab caption="%s">%s</a:tab>' % (self.server.resources.getResource('PROPERTIES', sLang), sProperties)

class Dlg_SelectContainer(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        rootFolder = self.server.store.getItem('')
        self.params = {
            'ROOT_ID': '/',
            'ROOT_IMG': rootFolder.__image__,
            'ROOT_DN': rootFolder.displayName.value,
            'ID': self.item.id,
            'SELECT_FOLDER': self.server.resources.getResource('SELECT_FOLDER', sLang),
            'CANCEL': self.server.resources.getResource('CANCEL', sLang),
            'OK': self.server.resources.getResource('OK', sLang)
        }
        sAction = self.request.queryString['action'][0]
        sTitle = self.server.resources.getResource(sAction.upper(), sLang)
        self.params['TITLE'] = sTitle + ' &quot;' + self.item.displayName.value + '&quot;'
        if sAction=='move':
            self.params['METHOD'] = 'moveTo'
        elif sAction=='restore':
            self.params['METHOD'] = 'restoreTo'
        else:
            self.params['METHOD'] = 'copyTo'


class Dlg_Rename(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        sRename = self.server.resources.getResource('RENAME', sLang)
        self.params = {
            'TITLE': sRename + ' &quot;' + self.item.displayName.value + '&quot;',
            'ENTER_NEW_NAME': self.server.resources.getResource('ENTER_NEW_NAME', sLang),
            'ID': self.item.id,
            'DN': self.item.displayName.value,
            'RENAME': sRename,
            'CANCEL': self.server.resources.getResource('CANCEL', sLang)
        }

#================================================================================
# Generic container interfaces
#================================================================================

class Frm_AutoNew(Frm_Auto):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        
        sLang = self.request.getLang()
        sCC = self.request.queryString['cc'][0]
        oNewItem = misc.getClassByName(sCC)()
        
        self.params = {
            'TITLE': '%s &quot;%s&quot;' % (self.server.resources.getResource('CREATE', sLang),
                    self.server.resources.getResource(oNewItem.contentclass, sLang)),
            'CREATE': self.server.resources.getResource('CREATE', sLang),
            'CANCEL': self.server.resources.getResource('CANCEL', sLang),
        
            'CC': sCC,
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'ICON': oNewItem.__image__,
            'PROPERTIES_TAB': '',
            'EXTRA_TABS': '',
            'SECURITY_TAB': self.getSecurity(self.item, True)
        }

        # inspect item properties
        sProperties = ''
        for attr_name in oNewItem.__props__:
            attr = getattr(oNewItem, attr_name)
            if isinstance(attr, datatypes.DataType):
                control, tab = self.getControlFromAttribute(attr_name, attr, False, True)
                sProperties += control
                self.params['EXTRA_TABS'] += tab
        
        self.params['PROPERTIES_TAB'] = '<a:tab caption="%s">%s</a:tab>' % (self.server.resources.getResource('PROPERTIES', sLang), sProperties)

class Dlg_SelectObjects(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        sCC = self.request.queryString['cc'][0]

        self.params = {
            'ID': self.item.id or '/',
            'IMG': self.item.__image__,
            'DN': self.item.displayName.value,
            'HAS_SUBFOLDERS': self.getStringFromBoolean(self.item.hasSubfolders()),
            'MULTIPLE': self.request.queryString['multiple'][0],
            'CC': sCC
        }

        oCmd = OqlCommand()
        sOql = "select * from '%s'" % self.item.id
        if sCC != '*':
            ccs = sCC.split('|')
            ccs = ["contentclass='%s'" % x for x in ccs]
            sConditions = " or ".join(ccs)
            sOql += " where %s" % sConditions
        oRes = oCmd.execute(sOql)

        sOptions = ''
        for obj in oRes:
             sOptions += '<a:option img="%s" value="%s" caption="%s"></a:option>' % (obj.__image__, obj.id, obj.displayName.value)
        self.params['OPTIONS'] = sOptions
        
class ContainerList(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        
        self.params = self.server.resources.getLocale(sLang).copy()
        
        self.params['ID'] = self.item.id
        self.params['PARENT_ID'] = self.item.parentid
        
#================================================================================
# Root Folder
#================================================================================

class Desktop(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()        
        self.params = {
            'LOGOFF': self.server.resources.getResource('LOGOFF', sLang),
            'LOGOFF?': self.server.resources.getResource('LOGOFF?', sLang),
            'START': self.server.resources.getResource('START', sLang),
            'APPLICATIONS': self.server.resources.getResource('APPLICATIONS', sLang),
            'SETTINGS': self.server.resources.getResource('SETTINGS', sLang),
            'INFO': self.server.resources.getResource('INFO', sLang),
            'USER': self.session.user.displayName.value,
            'ROOT': self.item.displayName.value,
            'RECYCLE_BIN': ''
        }
        # has the user access to recycle bin?
        rb = self.server.store.getItem('rb')
        if rb:
            self.params['RECYCLE_BIN'] = '''
                <a:icon top="80" left="10" width="80" height="80"
                    imgalign="top" ondblclick="generic.openContainer"
                    img="images/trashcan_full.gif" color="white"
                    caption="%s">
                        <a:prop name="folderID" value="rb"></a:prop>
                </a:icon>
            ''' % rb.displayName.value
        
        # get applications
        oCmd = OqlCommand()
        sOql = "select id,displayName,icon from 'apps' order by displayName asc"
        apps = oCmd.execute(sOql)
        sApps = ''
        if len(apps) > 0:
            for app in apps:
                sApps += '<a:menuoption img="%s" caption="%s" onclick="generic.runApp"><a:prop name="ID" value="%s"></a:prop></a:menuoption>' % (app['icon'], app['displayName'], app['id'])
            self.params['APPS'] = sApps
        else:
            self.params['APPS'] = '<a:menuoption caption="%s" disabled="true"></a:menuoption>' % self.server.resources.getResource('EMPTY', sLang)

class LoginPage(PorcupineDesktopServlet):
    def setParams(self):
        self.isPage = True
        
        sLang = self.request.getLang()
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '?cmd=login',
            'LOGIN_FAILED': self.server.resources.getResource('LOGIN_FAILED', sLang),
            'LOGIN': self.server.resources.getResource('LOGIN', sLang),
    
            'CLOSE': self.server.resources.getResource('CLOSE', sLang),
            'CANCEL': self.server.resources.getResource('CANCEL', sLang),
            'YES': self.server.resources.getResource('YES', sLang),
            'NO': self.server.resources.getResource('NO', sLang)
        }

class AboutDialog(XULServlet):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        self.params = {'VERSION': self.server.version}

#================================================================================
# Recycle Bin
#================================================================================

class RecycleList(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        
        self.params = self.server.resources.getLocale(sLang).copy()
        self.params ['ID'] = self.item.id


#================================================================================
# Applications folder
#================================================================================

class Frm_AppNew(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        
        sLang = self.request.getLang()
        oApp = common.Application()
        self.params = {
            'CC': oApp.contentclass,
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'ICON': oApp.__image__,
            'SECURITY_TAB': self.getSecurity(self.item, True)
        }

#================================================================================
# Users and groups folder
#================================================================================

class Frm_UserGroupNew(XULServlet):
    def setParams(self):
        sCC = self.request.queryString['cc'][0]
        self.params['FORM'] = ''
        if sCC == 'schemas.org.innoscript.security.User':
            servlet = Frm_UserNew(self.server, self.session, self.request)
            self.params['FORM'] = servlet.execute()
        elif sCC == 'schemas.org.innoscript.security.Group':
            servlet = Frm_GroupNew(self.server, self.session, self.request)
            self.params['FORM'] = servlet.execute()

class Frm_UserNew(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setExpiration(1200)
        
        oUser = security.User()
        self.params['CC'] = oUser.contentclass
        self.params['URI'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id
        self.params['REL_CC'] = '|'.join(oUser.memberof.relCc)
        self.params['ICON'] = oUser.__image__

        self.params['SELECT_FROM_POLICIES'] = self.request.serverVariables['SCRIPT_NAME'] + '/policies'
        self.params['POLICIES_REL_CC'] = '|'.join(oUser.policies.relCc)

        self.params['SECURITY_TAB'] = self.getSecurity(self.item, True)
        
class Frm_GroupNew(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setExpiration(1200)

        oGroup = security.Group()
        self.params['CC'] = oGroup.contentclass
        self.params['URI'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id
        self.params['REL_CC'] = '|'.join(oGroup.members.relCc)
        self.params['ICON'] = oGroup.__image__

        self.params['SELECT_FROM_POLICIES'] = self.request.serverVariables['SCRIPT_NAME'] + '/policies'
        self.params['POLICIES_REL_CC'] = '|'.join(oGroup.policies.relCc)

        self.params['SECURITY_TAB'] = self.getSecurity(self.item, True)

#================================================================================
# Group     
#================================================================================

class Frm_GroupProperties(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()

        user = self.session.user
        iUserRole = objectAccess.getAccess(self.item, user)
        readonly = (iUserRole==1)

        self.params['ID'] = self.item.id
        self.params['URI'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id
        self.params['ICON'] = self.item.__image__

        self.params['SELECT_FROM_POLICIES'] = self.request.serverVariables['SCRIPT_NAME'] + '/policies'
        self.params['POLICIES_REL_CC'] = '|'.join(self.item.policies.relCc)
        
        self.params['NAME'] = self.item.displayName.value
        self.params['DESCRIPTION'] = self.item.description.value
        self.params['MODIFIED'] = date.Date(self.item.modified).format(DATES_FORMAT, sLang)
        self.params['MODIFIED_BY'] = self.item.modifiedBy
        self.params['CONTENTCLASS'] = self.item.contentclass
        
        self.params['SELECT_FROM'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.parentid
        self.params['REL_CC'] = '|'.join(self.item.members.relCc)
        self.params['READONLY'] = self.getStringFromBoolean(readonly)
        
        members_options = ''
        members = self.item.members.getItems()
        for user in members:
            members_options += '<a:option img="%s" value="%s" caption="%s"></a:option>' % (user.__image__, user.id, user.displayName.value)
        self.params['MEMBERS_OPTIONS'] = members_options

        self.params['SECURITY_TAB'] = self.getSecurity(self.item)

#================================================================================
# Deleted Item
#================================================================================

class Frm_DeletedItem(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'ICON': self.item.__image__,
            'NAME': self.item.originalName,
            'LOC': self.item.originalLocation,
            'MODIFIED': date.Date(self.item.modified).format(DATES_FORMAT, sLang),
            'MODIFIED_BY': self.item.modifiedBy,
            'CONTENTCLASS': self.item.getDeletedItem().contentclass
        }

#================================================================================
# User     
#================================================================================
    
class Frm_UserResetPassword(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'TITLE': 'Reset password for user \'%s\'' % self.item.displayName.value,
            'OK': self.server.resources.getResource('OK', sLang),
            'CANCEL': self.server.resources.getResource('CANCEL', sLang)
        }
        
class Frm_UserProperties(PorcupineDesktopServlet):
    def setParams(self):
        sLang = self.request.getLang()

        user = self.session.user
        iUserRole = objectAccess.getAccess(self.item, user)
        readonly = (iUserRole==1)

        self.params['ID'] = self.item.id
        self.params['URI'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id
        self.params['ICON'] = self.item.__image__
        
        self.params['NAME'] = self.item.displayName.value
        self.params['FULL_NAME'] = self.item.fullName.value
        self.params['DESCRIPTION'] = self.item.description.value
        self.params['MODIFIED'] = date.Date(self.item.modified).format(DATES_FORMAT, sLang)
        self.params['MODIFIED_BY'] = self.item.modifiedBy
        self.params['CONTENTCLASS'] = self.item.contentclass
        
        self.params['SELECT_FROM'] = self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.parentid
        self.params['REL_CC'] = '|'.join(self.item.memberof.relCc)

        self.params['SELECT_FROM_POLICIES'] = self.request.serverVariables['SCRIPT_NAME'] + '/policies'
        self.params['POLICIES_REL_CC'] = '|'.join(self.item.policies.relCc)

        self.params['READONLY'] = self.getStringFromBoolean(readonly)
        
        memberof_options = ''
        memberof = self.item.memberof.getItems()
        for group in memberof:
            memberof_options += '<a:option img="%s" value="%s" caption="%s"></a:option>' % (group.__image__, group.id, group.displayName.value)
        self.params['MEMBER_OF_OPTIONS'] = memberof_options
        
        self.params['SECURITY_TAB'] = self.getSecurity(self.item)

#================================================================================
# Application
#================================================================================

class Frm_AppProperties(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setHeader('Cache-Control', 'no-cache')
        sLang = self.request.getLang()

        user = self.session.user
        iUserRole = objectAccess.getAccess(self.item, user)
        readonly = (iUserRole==1)

        self.params = {
            'ID': self.item.id,
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'IMG': self.item.__image__,
            'NAME': self.item.displayName.value,
            'DESCRIPTION': self.item.description.value,
            'ICON': self.item.icon.value,
            'INTERFACE': xmlUtils.XMLEncode(self.item.interface.value),
            'SCRIPT': xmlUtils.XMLEncode(self.item.script.value),
            'IS_RESIZABLE': self.getStringFromBoolean(self.item.isResizable.value),
            'CAN_MINIMIZE': self.getStringFromBoolean(self.item.canMinimize.value),
            'CAN_MAXIMIZE': self.getStringFromBoolean(self.item.canMaximize.value),
            'LEFT': self.item.left.value,
            'TOP': self.item.top.value,
            'WIDTH': self.item.width.value,
            'HEIGHT': self.item.height.value,
            'MODIFIED': date.Date(self.item.modified).format(DATES_FORMAT, sLang),
            'MODIFIED_BY': self.item.modifiedBy,
            'CONTENTCLASS': self.item.contentclass,
            'SECURITY_TAB': self.getSecurity(self.item),
            'READONLY': self.getStringFromBoolean(readonly)
        }

class Run_App(HTTPServlet):
    def execute(self):
        self.response.setExpiration(1200)
        self.response.content_type = 'text/xml';
        rootUri = self.request.serverVariables['SCRIPT_NAME']

        sInterface = self.item.getInterface(rootUri)
        sLang = self.request.getLang()
        dctLocale = self.server.resources.getLocale(sLang)
        self.response.write(sInterface % dctLocale)
        
class GetAppScript(HTTPServlet):
    def execute(self):
        self.response.setExpiration(1200)
        sLang = self.request.getLang()
        dctLocale = self.server.resources.getLocale(sLang)
        self.response.content_type = 'text/javascript'
        self.response.write(self.item.script.value % dctLocale)
