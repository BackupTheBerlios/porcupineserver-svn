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
Generic Session Manager classes.
Use these as base classes to implement your own session managers.
"""

import time

from porcupine.config.services import services
from porcupine import serverExceptions
from porcupine.security import sessionManager
from porcupine.security import session
from porcupine.db import db
from porcupine.services import management
from porcupine.utils import misc

class GenericSessionManager(object):
    def __init__(self):
        self.sessionClass = session.Session
        self.supports_replication = False

    def createSession(self, user):
        session = self.sessionClass(misc.generateGUID(), user, {})
        return session

    # to be implemented by subclass
    def getSession(self, sessionid):
        pass

    def putSession(self, session):
        pass

    def removeSession(self, sessionid):
        pass

    def close(self):
        pass

class SessionManagerReplicator(object):
    def __init__(self):
        self.sessionClass = session.ReplSession
        self.__locks = 0
        self.supports_replication = True

    def lock(self):
        self.__locks += 1

    def unlock(self):
        if self.__locks:
            self.__locks -= 1

    def waitForUnlock(self):
        while self.__locks:
            time.sleep(1)

    def createSession(self, user):
        # session creation is allowed only on masters
        if services['management'].isMaster():
            self.waitForUnlock()
            oNewSession = super(SessionManagerReplicator, self).createSession(user)
            # replicate session
            services['management'].sendMessage(management.REP_BROADCAST, 'NEW_SESSION',
                                               (oNewSession.sessionid,
                                                user._id,
                                                oNewSession.getData()))
            return(oNewSession)
        else:
            raise serverExceptions.ProxyRequest

    def removeSession(self, sessionid):
        self.waitForUnlock()
        super(SessionManagerReplicator, self).removeSession(sessionid)
        # replicate deletion
        services['management'].sendMessage(management.REP_BROADCAST, 'DEL_SESSION',
                                           sessionid)

    # generator function
    # used by replication service during host synchronization
    def enumerate(self):
        for sessionid in sessionManager._sessionList:
            oSession = self.getSession(sessionid)
            yield((sessionid, oSession.user._id, oSession.getData()))

    # these methods are called by replicator service
    # and are executed only on replicas....

    def repl_addSession(self, sessionid, userid, data):
        print 'got new session: ' + sessionid
        # create new session
        oNewSession = self.sessionClass(sessionid, db.getItem(userid), data)
        self.putSession(oNewSession)
        sessionManager._sessionList.append(sessionid)

    def repl_removeSession(self, sessionid):
        super(SessionManagerReplicator, self).removeSession(sessionid)
        sessionManager._sessionList.remove(sessionid)

    def repl_keepAlive(self, sessionid):
        oSession = self.getSession(sessionid)
        # call superclass keepAlive in order
        # not to send 'KEEP_ALIVE' again
        super(self.sessionClass, oSession).keepAlive()

    def repl_setUser(self, sessionid, userid):
        oUser = db.getItem(userid)
        oSession = self.getSession(sessionid)
        # call superclass setUser in order
        # not to raise a ProxyRequest exception again
        super(self.sessionClass, oSession).setUser(oUser)

    def repl_setValue(self, sessionid, name, value):
        oSession = self.getSession(sessionid)
        # call superclass setValue in order
        # not to raise a ProxyRequest exception again
        super(self.sessionClass, oSession).setValue(name, value)
