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
In-memory session manager classes for single-server and replicated environments
"""

from porcupine.security import genericSessionManager

class SessionManager(genericSessionManager.GenericSessionManager):
    def __init__(self):
        self.activeSessions = {}
        genericSessionManager.GenericSessionManager.__init__(self)

    def getSession(self, sessionid):
        session = self.activeSessions.get(sessionid, None)
        return(session)

    def putSession(self, session):
        self.activeSessions[session.sessionid] = session

    def removeSession(self, sessionid):
        del self.activeSessions[sessionid]

class XSessionManager(genericSessionManager.SessionManagerReplicator, SessionManager):
    def __init__(self):
        SessionManager.__init__(self)
        genericSessionManager.SessionManagerReplicator.__init__(self)
