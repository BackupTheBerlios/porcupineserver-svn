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
"Porcupine Server Thread"

import re

from porcupine.core import psp, response, serverProxy
from porcupine import serverExceptions
from porcupine.core.asyncBaseServer import BaseServerThread 
from porcupine.config import serverSettings
from porcupine.config.requesttypes import requestInterfaces
from porcupine.config import registrations
from porcupine.security import sessionManager
from porcupine.db import db

SESSIONID = re.compile('/\{([a-f0-9]{32})\}')

class PorcupineThread(BaseServerThread):
    def __init__(self, target, name):
        BaseServerThread.__init__(self, target, name)
        self.request = None
        self.session = None
        self.trans = None

    def getResponse(self):
        # get request parameters
        sMethod = self.request.serverVariables['REQUEST_METHOD']
        sBrowser = self.request.serverVariables['HTTP_USER_AGENT']
        sLang = self.request.getLang()
        sPath = self.request.serverVariables.setdefault('PATH_INFO', '/')

        self.response = response.BaseResponse()

        servlet = None
        sAction = None
        self.request.item = None
        registration = None
        
        try:
            try:
                oSessionMatch = re.match(SESSIONID, sPath)
                if oSessionMatch:
                    oSession = sessionManager.fetchSession(oSessionMatch.group(1))
                    sPath = sPath.replace(oSessionMatch.group(), '', 1) or '/'
                    if oSession:
                        self.session = oSession
                        
                        if not oSession.sessionid in self.request.serverVariables["SCRIPT_NAME"]:
                            self.request.serverVariables["SCRIPT_NAME"] += '/{%s}' % oSession.sessionid
                        else:
                            lstScript = self.request.serverVariables["SCRIPT_NAME"].split('/')
                            self.request.serverVariables["SCRIPT_NAME"] = "/%s/{%s}" %(lstScript[1], oSession.sessionid)
                        
                        self.request.serverVariables["AUTH_USER"] = oSession.user.displayName.value
                        oUser = oSession.user
                    else:
                        # invalid sesionid
                        # create new session and redirect
                        self.createGuestSessionAndRedirect(sPath)
                else:
                    self.createGuestSessionAndRedirect(sPath)

                try:
                    self.request.item = db.getItem(sPath)
                    # db request
                    sItemCC = self.request.item.getContentclass()
                    # get cmd parameter
                    sCmd = self.request.queryString.setdefault('cmd',[''])[0]
                    registration = registrations.storeConfig.getRegistration(
                        sItemCC, sMethod, sCmd, sBrowser, sLang)
    
                    if not(serverSettings.allow_guests or \
                            hasattr(oUser, 'authenticate')) and \
                            serverSettings.login_page != (sPath + \
                            self.request.getQueryString())[:len(serverSettings.login_page)]:
                        sLoginUrl = self.request.getRootUrl() + serverSettings.login_page
                        self.response.redirect(sLoginUrl)

                    if not registration:
                        raise serverExceptions.NoViewRegistered
    
                except serverExceptions.DBItemNotFound:
                    # app request
                    lstPath = sPath.split('/')
                    appName = lstPath[1]
                    # remove blank entry & app name to get the requested path
                    sAppPath = '/'.join(lstPath[2:])
                    webApp = registrations.apps.setdefault(appName, None)
                    if webApp:
                        registration = webApp.getRegistration(
                            sAppPath, sMethod, sBrowser, sLang)
                    if not registration:
                        raise serverExceptions.ItemNotFound, \
                            'The resource "%s" does not exist' % sPath
                
                rtype = registration.type

                if rtype == 2: #servlet
                    servlet = registration.context(serverProxy.proxy, oSession, self.request)
                    servlet.execute()
                elif rtype == 1: # psp page
                    servlet = psp.PspExecutor(serverProxy.proxy, oSession, self.request)
                    servlet.execute(registration.context)
                elif rtype == 0: # static file
                    self.response.loadFromFile(registration.context)
                    if registration.encoding:
                        self.response.charset = registration.encoding
            
            except serverExceptions.ResponseEnd, e:
                pass

            if registration:
                # apply post-processing filters
                dummy = [
                    filter.apply(self.response, self.request, registration)
                    for filter in registration.filters
                ]

        except serverExceptions.PorcupineException, e:
            self.response._writeError(e)
            if e.severity:
                e.writeToLog()
        except serverExceptions.ProxyRequest, e:
            raise e
        except:
            e = serverExceptions.InternalServerError()
            self.response._writeError(e)
            if e.severity:
                e.writeToLog()

        # abort uncommited transaction
        if self.trans and not self.trans._iscommited:
            self.trans.abort()

        self.trans = None

        # restore original user in case of runAsSystem
        if servlet and self.session.user.id == 'system':
            self.session.user = oUser

        requestInterfaces[self.request.interface](self.requestHandler, self.response)

    def createGuestSessionAndRedirect(self, sPath):
        # create new session with the specified guest user
        oGuest = db.getItem(serverSettings.guest_account)
        oNewSession = sessionManager.create(oGuest)
        self.response.redirect(
            '%s/{%s}%s%s' % (
                self.request.getRootUrl()
                ,oNewSession.sessionid
                ,sPath
                ,self.request.getQueryString()
            )
        )
