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
In-memory session manager class
"""
from porcupine.security.genericSessionManager import GenericSessionManager

class SessionManager(GenericSessionManager):
    def __init__(self):
        self.activeSessions = {}
        GenericSessionManager.__init__(self)

    def getSession(self, sessionid):
        session = self.activeSessions.get(sessionid, None)
        return(session)

    def putSession(self, session):
        self.activeSessions[session.sessionid] = session

    def removeSession(self, sessionid):
        del self.activeSessions[sessionid]

