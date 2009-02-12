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
Porcupine in memory session manager classes
"""
import time
import logging
from threading import Thread

from porcupine.utils import misc
from porcupine.core.session.genericsessionmanager import GenericSessionManager
from porcupine.core.session.genericsession import GenericSession

class SessionManager(GenericSessionManager):
    """
    In memory session manager implementation class
    """
    def __init__(self, timeout):
        GenericSessionManager.__init__(self, timeout)
        self._sessions = {}
        self._list = []
        self._is_active = True
        self._expire_thread = Thread(target=self._expire_sessions,
                                     name='Session expriration thread')
        self._expire_thread.start()

    def _expire_sessions(self):
        logger = logging.getLogger('serverlog')
        while self._is_active:
            for sessionid in self._list:
                session = self.get_session(sessionid, revive=False)
                if time.time() - session._last_accessed > self.timeout:
                    logger.debug('Expiring Session: %s' % sessionid)
                    session.terminate()
                    logger.debug('Total active sessions: %s' % \
                                 str(len(self._list)))
                else:
                    break
            time.sleep(1.0)

    def create_session(self, userid):
        session = Session(userid, {})
        self._sessions[session.sessionid] = session
        self._list.append(session.sessionid)
        return session

    def get_session(self, sessionid, revive=True):
        session = self._sessions.get(sessionid, None)
        if session and revive:
            # move sessionid at the end of the list
            self._list.append(session.sessionid)
            self._list.remove(session.sessionid)
            # update last access time
            session._last_accessed = time.time()
        return session

    def remove_session(self, sessionid):
        self._list.remove(sessionid)
        del self._sessions[sessionid]

    def close(self):
        self._is_active = False
        if self._expire_thread.isAlive():
            self._expire_thread.join()
        # remove temporary files
        for sessionid in self._list:
            self._sessions.get(sessionid).remove_temp_files()

class Session(GenericSession):
    """
    Session class for the in memory session manager
    """
    def __init__(self, userid, sessiondata):
        GenericSession.__init__(self, misc.generateGUID(), userid)
        self._last_accessed = time.time()
        self.__data = sessiondata

    def setValue(self, name, value):
        self.__data[name] = value

    def getValue(self, name):
        return self.__data.get(name, None)

    def get_data(self):
        return(self.__data)
