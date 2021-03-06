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
Web methods for the root folder class
"""
import os
import base64

from porcupine import db
from porcupine import HttpContext
from porcupine import webmethods
from porcupine import filters

from porcupine.oql.command import OqlCommand
from org.innoscript.desktop.schema.common import RootFolder

DESKSTOP_PANE = '''<rect height="-1" overflow="hidden">
    <icon top="10" left="10" width="80" height="80" imgalign="top"
                ondblclick="generic.openContainer" img="desktop/images/store.gif"
                color="white" caption="%s">
            <prop name="folderID" value=""></prop>
    </icon>
    %s
</rect>'''

@filters.runas('system')
@webmethods.remotemethod(of_type=RootFolder)
def login(self, username, password):
    "Remote method for authenticating users"
    http_context = HttpContext.current()
    users_container = db.getItem('users')
    user = users_container.getChildByName(username)
    if user and hasattr(user, 'authenticate'):
        if user.authenticate(password):
            http_context.session.userid = user.id
            return True
    return False

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=RootFolder, isPage=True,
                   template='../ui.LoginPage.quix')
def login(self):
    "Displays the login page"
    return {
        'URI': HttpContext.current().request.SCRIPT_NAME or '.'
    }
    
@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=RootFolder,
                   template='../ui.Dlg_LoginAs.quix')
def loginas(self):
    "Displays the login as dialog"
    return {
        'URI': HttpContext.current().request.SCRIPT_NAME + '/?cmd=login'
    }

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=RootFolder,
                   template='../ui.AboutDialog.quix')
def about(self):
    "Displays the about dialog"
    context = HttpContext.current()
    context.response.setExpiration(1200)
    return {'VERSION': context.server.version}

@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=RootFolder,
                   template='../ui.Dlg_UserSettings.quix')
def user_settings(self):
    "Displays the user settings dialog"
    context = HttpContext.current()
    context.response.setHeader('cache-control', 'no-cache')
    
    settings = context.user.settings
    taskbar_pos = settings.value.setdefault('TASK_BAR_POS', 'bottom')
    
    params = {'TASK_BAR_POS' : taskbar_pos}
    
    if taskbar_pos == 'bottom':
        params['CHECKED_TOP'] = 'false'
        params['CHECKED_BOTTOM'] = 'true'
    else:
        params['CHECKED_TOP'] = 'true'
        params['CHECKED_BOTTOM'] = 'false'
        
    autoRun = settings.value.setdefault('AUTO_RUN', '')
        
    if settings.value.setdefault('RUN_MAXIMIZED', False) == True:
        params['RUN_MAXIMIZED_VALUE'] = 'true'
    else:
        params['RUN_MAXIMIZED_VALUE'] = 'false'

    # get applications
    oCmd = OqlCommand()
    sOql = "select displayName,launchUrl,icon from 'apps' " + \
           "order by displayName asc"
    apps = oCmd.execute(sOql)
    
    sSelected = ''
    if autoRun == '':
        sSelected = 'true'
    
    sApps = '<option caption="@@NONE_APP@@" selected="%s" value=""/>' \
            % sSelected
    if len(apps) > 0:
        for app in apps:
            if autoRun == app['launchUrl']:
                sSelected = 'true'
            else:
                sSelected = 'false'
            sApps += \
             '<option img="%s" caption="%s" value="%s" selected="%s"/>' % \
             (app['icon'], app['displayName'], app['launchUrl'], sSelected)
    params['APPS'] = sApps
    
    return params

@filters.runas('system')
@webmethods.remotemethod(of_type=RootFolder)
@db.transactional(auto_commit=True)
def applySettings(self, data):
    "Saves user's preferences"
    context = HttpContext.current()
    activeUser = context.original_user
    for key in data:
        activeUser.settings.value[key] = data[key]
    txn = db.getTransaction()
    activeUser.update(txn)
    return True

@filters.requires_login('/?cmd=login')
@filters.i18n('org.innoscript.desktop.strings.resources')
@webmethods.quixui(of_type=RootFolder,
                   isPage=True,
                   template='../ui.Desktop.quix')
def __blank__(self):
    "Displays the desktop"
    context = HttpContext.current()
    context.response.setHeader('cache-control', 'no-cache')
    
    oUser = context.user
    
    params = {
        'USER' : oUser.displayName.value,
        'AUTO_RUN' : '',
        'RUN_MAXIMIZED' : 0,
        'SETTINGS_DISABLED' : '',
        'LOGOFF_DISABLED' : ''
    }
    if hasattr(oUser, 'authenticate'):
        settings = oUser.settings
        params['AUTO_RUN'] = \
            settings.value.setdefault('AUTO_RUN', '')
        params['RUN_MAXIMIZED'] = \
            int(settings.value.setdefault('RUN_MAXIMIZED', False))
        taskbar_position = \
            settings.value.setdefault('TASK_BAR_POS', 'bottom')
    else:
        taskbar_position = 'bottom'
        params['SETTINGS_DISABLED'] = 'true'
        params['LOGOFF_DISABLED'] = 'true'
    
    params['REPOSITORY_DISABLED'] = 'true'
    params['PERSONAL_FOLDER'] = ''
    if hasattr(oUser, 'personalFolder'):
        params['REPOSITORY_DISABLED'] = 'false'
        params['PERSONAL_FOLDER'] = oUser.personalFolder.value
    
    # has the user access to recycle bin?
    rb_icon = ''
    rb = db.getItem('rb')
    if rb:
        rb_icon = '''
            <icon top="80" left="10" width="80" height="80"
                imgalign="top" ondblclick="generic.openContainer"
                img="desktop/images/trashcan_full.gif" color="white"
                caption="%s">
                    <prop name="folderID" value="rb"></prop>
            </icon>
        ''' % rb.displayName.value
    
    desktop_pane = DESKSTOP_PANE % (self.displayName.value, rb_icon)
    
    if taskbar_position == 'bottom':
        params['TOP'] = desktop_pane
        params['BOTTOM'] = ''
    else:
        params['TOP'] = ''
        params['BOTTOM'] = desktop_pane
    
    # get applications
    oCmd = OqlCommand()
    sOql = "select launchUrl,displayName,icon from 'apps' " + \
           "order by displayName asc"
    apps = oCmd.execute(sOql)
    sApps = ''
    if len(apps) > 0:
        for app in apps:
            sApps += '''<menuoption img="%s" caption="%s"
                onclick="generic.runApp">
                    <prop name="url" value="%s"></prop>
                </menuoption>''' % \
                (app['icon'], app['displayName'], app['launchUrl'])
        params['APPS'] = sApps
    else:
        params['APPS'] = '<menuoption caption="@@EMPTY@@"' + \
                         ' disabled="true"></menuoption>'

    return params

@webmethods.webmethod(of_type=RootFolder,
                      template='../browsernotsuppoted.htm')
def __blank__(self):
    "Displays the browser not supported HTML page"
    return {
        'USER_AGENT' : HttpContext.current().request.HTTP_USER_AGENT
    }

@webmethods.remotemethod(of_type=RootFolder)
def executeOqlCommand(self, command, range=None):
    oCmd = OqlCommand()
    oRes = oCmd.execute(command)
    if range == None:
        return [rec for rec in oRes]
    else:
        return [oRes[range[0]:range[1]], len(oRes)]

@webmethods.remotemethod(of_type=RootFolder)
def logoff(self):
    context = HttpContext.current()
    context.session.terminate()
    return True

@filters.requires_policy('uploadpolicy')
@webmethods.remotemethod(of_type=RootFolder)
def upload(self, chunk, fname):
    context = HttpContext.current()
    chunk = base64.decodestring(chunk)
    if not fname:
        fileno, fname = context.session.getTempFile()
        os.write(fileno, chunk)
        os.close(fileno)
        fname = os.path.basename(fname)
    else:
        tmpfile = file(context.server.temp_folder + '/' + fname, 'ab+')
        tmpfile.write(chunk)
        tmpfile.close()
    return fname