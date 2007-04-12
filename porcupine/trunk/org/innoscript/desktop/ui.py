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
"QuiX UIs"

from porcupine.core.servlet import HTTPServlet, XULSimpleTemplateServlet
from porcupine.oql.command import OqlCommand
from porcupine.security import objectAccess
from porcupine.utils import date, xmlUtils, misc
from porcupine import datatypes

from org.innoscript.desktop.strings import resources
from org.innoscript.desktop.schema import common, security

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
            '<a:button left="this.parent.getWidth()-20" top="center" img="desktop/images/cancel8.gif" width="20" height="20" disabled="%s" onclick="generic.clearReference1"></a:button>' +
        '</a:rect>',

    datatypes.ReferenceN: '''
        <a:tab caption="%s">
            <a:box width="100%%" height="100%%" orientation="v">
                <a:selectlist name="%s" multiple="true" posts="all" height="-1">
                    <a:prop name="SelectFrom" value="%s"></a:prop>
                    <a:prop name="RelatedCC" value="%s"></a:prop>
                    %s
                </a:selectlist>
                <a:rect height="24" disabled="%s">
                    <a:flatbutton width="70" height="22" caption="@@ADD@@..." onclick="generic.selectItems"></a:flatbutton>
                    <a:flatbutton left="80" width="70" height="22" caption="@@REMOVE@@" onclick="generic.removeSelectedItems"></a:flatbutton>
                </a:rect>
            </a:box>
        </a:tab>
        '''
}

SECURITY_TAB = '''
<a:tab caption="@@SECURITY@@" onactivate="generic.getSecurity">
    <a:box orientation="v" spacing="0" width="100%%" height="100%%">
        <a:field id="__rolesinherited"
            height="24"
            name="__rolesinherited"
            type="checkbox"
            value="%s"
            onclick="generic.rolesInherited_onclick"
            caption="@@ROLES_INHERITED@@"/>
        <a:box spacing="0" disabled="%s" height="-1">
            <a:datagrid id="__acl" name="__acl" width="-1">
                <a:listheader>
                    <a:column width="140" caption="@@displayName@@" name="displayName" editable="false" sortable="true"></a:column>
                    <a:column width="140" caption="@@ROLE@@" name="role" type="optionlist" sortable="true">
                        <a:option value="1" caption="@@ROLE_1@@"></a:option>
                        <a:option value="2" caption="@@ROLE_2@@"></a:option>
                        <a:option value="4" caption="@@ROLE_4@@"></a:option>
                        <a:option value="8" caption="@@ROLE_8@@"></a:option>
                    </a:column>
                </a:listheader>
            </a:datagrid>
            <a:rect width="60">
                <a:flatbutton left="center" width="56" height="22" caption="@@ADD@@" onclick="generic.addACLEntry"></a:flatbutton>
                <a:flatbutton top="24" left="center" width="56" height="22" caption="@@REMOVE@@" onclick="generic.removeACLEntry"></a:flatbutton>
            </a:rect>
        </a:box>
    </a:box>
</a:tab>
'''

DATES_FORMAT = 'ddd, dd month yyyy h12:min:sec MM'

DESKSTOP_PANE = '''<a:rect height="-1" overflow="hidden">
    <a:icon top="10"
            left="10"
            width="80"
            height="80"
            imgalign="top"
            ondblclick="generic.openContainer"
            img="desktop/images/store.gif"
            color="white"
            caption="%s">
            <a:prop name="folderID" value=""></a:prop>
    </a:icon>
    %s
</a:rect>'''

#================================================================================
# Generic functions
#================================================================================
class PorcupineDesktopServlet(XULSimpleTemplateServlet):        
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
            return SECURITY_TAB % (sChecked, sChecked)
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
        attrlabel = '@@%s@@' % attrname
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
                '|'.join(attr.relCc), options, self.getStringFromBoolean(readonly)
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
        
        self.params['PROPERTIES_TAB'] = '<a:tab caption="@@PROPERTIES@@">%s</a:tab>' % sProperties

class Dlg_SelectContainer(PorcupineDesktopServlet):
    def setParams(self):
        rootFolder = self.server.store.getItem('')
        self.params = {
            'ROOT_ID': '/',
            'ROOT_IMG': rootFolder.__image__,
            'ROOT_DN': rootFolder.displayName.value,
            'ID': self.item.id,
        }
        sAction = self.request.queryString['action'][0]
        self.params['TITLE'] = '@@%s@@' % sAction.upper()
        
        if sAction != 'select_folder':
            self.params['TITLE'] += ' &quot;' + self.item.displayName.value + '&quot;'
        
class Dlg_Rename(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        self.params = {
            'TITLE': self.item.displayName.value,
            'ID': self.item.id,
            'DN': self.item.displayName.value,
        }

#================================================================================
# Generic container interfaces
#================================================================================

class Frm_AutoNew(Frm_Auto):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        self.response.setExpiration(1200)
        
        sCC = self.request.queryString['cc'][0]
        oNewItem = misc.getCallableByName(sCC)()
        
        self.params = {
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
        
        self.params['PROPERTIES_TAB'] = '<a:tab caption="@@PROPERTIES@@">%s</a:tab>' % sProperties

class Dlg_SelectObjects(PorcupineDesktopServlet):
    def setParams(self):
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
        self.response.setExpiration(1200)
        self.params['ID'] = self.item.id
        self.params['PARENT_ID'] = self.item.parentid
        
#================================================================================
# Root Folder
#================================================================================

class Desktop(PorcupineDesktopServlet):
    def setParams(self):
        self.isPage = True
        self.response.setHeader('cache-control', 'no-cache')
        #sLang = self.request.getLang()
        oUser = self.session.user
        self.params = {
            'USER': oUser.displayName.value,
            'AUTO_RUN' : '',
            'RUN_MAXIMIZED' : 0,
            'SETTINGS_DISABLED' : '',
            'LOGOFF_DISABLED' : ''
        }
        if hasattr(oUser, 'authenticate'):
            self.params['AUTO_RUN'] = oUser.settings.value.setdefault('AUTO_RUN', '')
            self.params['RUN_MAXIMIZED'] = int(oUser.settings.value.setdefault('RUN_MAXIMIZED', False))
            taskbar_position = self.session.user.settings.value.setdefault('TASK_BAR_POS', 'bottom')
        else:
            taskbar_position = 'bottom'
            self.params['SETTINGS_DISABLED'] = 'true'
            self.params['LOGOFF_DISABLED'] = 'true'
        
        self.params['REPOSITORY_DISABLED'] = 'true'
        self.params['PERSONAL_FOLDER'] = ''
        if hasattr(oUser, 'personalFolder'):
            self.params['REPOSITORY_DISABLED'] = 'false'
            self.params['PERSONAL_FOLDER'] = oUser.personalFolder.value
        
        # has the user access to recycle bin?
        rb_icon = ''
        rb = self.server.store.getItem('rb')
        if rb:
            rb_icon = '''
                <a:icon top="80" left="10" width="80" height="80"
                    imgalign="top" ondblclick="generic.openContainer"
                    img="desktop/images/trashcan_full.gif" color="white"
                    caption="%s">
                        <a:prop name="folderID" value="rb"></a:prop>
                </a:icon>
            ''' % rb.displayName.value
        
        desktop_pane = DESKSTOP_PANE % (self.item.displayName.value, rb_icon)
        
        if taskbar_position == 'bottom':
            self.params['TOP'] = desktop_pane
            self.params['BOTTOM'] = ''
        else:
            self.params['TOP'] = ''
            self.params['BOTTOM'] = desktop_pane
        
        # get applications
        oCmd = OqlCommand()
        sOql = "select launchUrl,displayName,icon from 'apps' order by displayName asc"
        apps = oCmd.execute(sOql)
        sApps = ''
        if len(apps) > 0:
            for app in apps:
                sApps += '<a:menuoption img="%s" caption="%s" onclick="generic.runApp"><a:prop name="url" value="%s"></a:prop></a:menuoption>' % (app['icon'], app['displayName'], app['launchUrl'])
            self.params['APPS'] = sApps
        else:
            self.params['APPS'] = '<a:menuoption caption="@@EMPTY@@" disabled="true"></a:menuoption>'

class LoginPage(XULSimpleTemplateServlet):
    def setParams(self):
        self.isPage = True
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '?cmd=login'
        }

class Dlg_LoginAs(XULSimpleTemplateServlet):
    def setParams(self):
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '?cmd=login'
        }

class AboutDialog(XULSimpleTemplateServlet):
    def setParams(self):
        self.response.setExpiration(1200)
        self.params = {'VERSION': self.server.version}

class Dlg_UserSettings(XULSimpleTemplateServlet):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
        #sLang = self.request.getLang()
        
        self.params['TASK_BAR_POS'] = self.session.user.settings.value.setdefault('TASK_BAR_POS', 'bottom')
        
        if self.params['TASK_BAR_POS'] == 'bottom':
            self.params['CHECKED_TOP'] = 'false'
            self.params['CHECKED_BOTTOM'] = 'true'
        else:
            self.params['CHECKED_TOP'] = 'true'
            self.params['CHECKED_BOTTOM'] = 'false'
            
        autoRun = self.session.user.settings.value.setdefault('AUTO_RUN', '')
            
        if self.session.user.settings.value.setdefault('RUN_MAXIMIZED', False) == True:
            self.params['RUN_MAXIMIZED_VALUE'] = 'true'
        else:
            self.params['RUN_MAXIMIZED_VALUE'] = 'false'

        # get applications
        oCmd = OqlCommand()
        sOql = "select displayName,launchUrl,icon from 'apps' order by displayName asc"
        apps = oCmd.execute(sOql)
        
        sSelected = ''
        if autoRun == '':
            sSelected = 'true'
        
        sApps = '<a:option caption="@@NONE_APP@@" selected="%s" value=""/>' % sSelected
        if len(apps) > 0:
            for app in apps:
                if autoRun == app['launchUrl']:
                    sSelected = 'true'
                else:
                    sSelected = 'false'
                sApps += '<a:option img="%s" caption="%s" value="%s" selected="%s"/>' % (app['icon'], app['displayName'], app['launchUrl'], sSelected)
            self.params['APPS'] = sApps

#================================================================================
# Recycle Bin
#================================================================================

class RecycleList(XULSimpleTemplateServlet):
    def setParams(self):
        self.response.setExpiration(1200)
        self.params['ID'] = self.item.id


#================================================================================
# Applications folder
#================================================================================

class Frm_AppNew(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setExpiration(1200)
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
        self.response.setHeader('cache-control', 'no-cache')
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

class Frm_DeletedItem(XULSimpleTemplateServlet):
    def setParams(self):
        sLang = self.request.getLang()
        self.params = {
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
    
class Frm_UserResetPassword(XULSimpleTemplateServlet):
    def setParams(self):
        self.params = {
            'URI': self.request.serverVariables['SCRIPT_NAME'] + '/' + self.item.id,
            'TITLE': self.item.displayName.value
        }
        
class Frm_UserProperties(PorcupineDesktopServlet):
    def setParams(self):
        self.response.setHeader('cache-control', 'no-cache')
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
            'LAUNCH_URL': xmlUtils.XMLEncode(self.item.launchUrl.value),
            'MODIFIED': date.Date(self.item.modified).format(DATES_FORMAT, sLang),
            'MODIFIED_BY': self.item.modifiedBy,
            'CONTENTCLASS': self.item.contentclass,
            'SECURITY_TAB': self.getSecurity(self.item),
            'READONLY': self.getStringFromBoolean(readonly)
        }



