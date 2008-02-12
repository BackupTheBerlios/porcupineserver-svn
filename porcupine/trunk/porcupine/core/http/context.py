#===============================================================================
#    Copyright 2005-2007 Tassos Koutsovassilis
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
"Http context class"
import re

from porcupine.core import serverProxy
from porcupine.security import SessionManager
from porcupine.config.settings import settings
from porcupine.db import db

class HttpContext(object):
    """Http context class
    
    @cvar server: Gives access to the server utility object,
                  which among others includes the server's
                  database handle.
    @type server: L{Server<porcupine.core.serverProxy.Server>}
    
    @ivar session: The current session object
    @type session: L{Session<porcupine.security.session.Session>}
    
    @ivar request: The current request object
    @type request: L{Request<porcupine.core.http.request.HttpRequest>}
    
    @ivar response: The current response object
    @type response: L{Request<porcupine.core.http.response.HttpResponse>}
    """
    sid_pattern = re.compile('/\{([a-f0-9]{32})\}')
    server = serverProxy.Server()
    def __init__(self, request=None, response=None):
        self.request = request
        self.response = response
        self.session = None
        
        if request:
            path_info = request.serverVariables['PATH_INFO'] or '/'
            
            # get session
            session = None
            
            cookiesEnabled = True
            if request.cookies.has_key('_sid'):
                session = SessionManager.fetchSession(request.cookies['_sid'].value)
            else:
                cookiesEnabled = False
                session_match = re.match(self.sid_pattern, path_info)
                if session_match:
                    path_info = path_info.replace(session_match.group(), '', 1) or '/'
                    request.serverVariables['PATH_INFO'] = path_info
                    session = SessionManager.fetchSession(session_match.group(1))
            
            if session != None:
                self.session = session
                request.serverVariables["AUTH_USER"] = session.user.displayName.value
                
                if not cookiesEnabled:
                    if not session.sessionid in request.serverVariables["SCRIPT_NAME"]:
                        request.serverVariables["SCRIPT_NAME"] += '/{%s}' % session.sessionid
                    else:
                        lstScript = request.serverVariables["SCRIPT_NAME"].split('/')
                        request.serverVariables["SCRIPT_NAME"] = \
                            "/%s/{%s}" %(lstScript[1], session.sessionid)
            else:
                self.session = self.__create_guest_session()

    def __create_guest_session(self):
        # create new session with the specified guest user
        guest_user = db.getItem(settings['sessionmanager']['guest'])
        new_session = SessionManager.create(guest_user)
        
        session_id = new_session.sessionid
        query_string = self.request.getQueryString()
        
        if '_nojavascript' in query_string:
            root_url = self.request.getRootUrl()
            path = self.request.serverVariables['PATH_INFO']
            self.context.response.redirect(
                '%(root_url)s/{%(session_id)s}%(path)s' % locals()
            )
        
        # add cookie with sessionid
        self.response.cookies['_sid'] = session_id
        self.response.cookies['_sid']['path'] = \
            self.request.serverVariables['SCRIPT_NAME']
        return new_session