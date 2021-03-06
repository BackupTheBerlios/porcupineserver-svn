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
"Porcupine Server session manager"

import time, logging
from threading import Thread

timeout = 1200
isActive = True
_sessionList = []
sessionExpireThread = None
sm = None

def open(smClass, session_timeout):
    global timeout, sm, sessionExpireThread, isActive, _sessionList
    timeout = session_timeout
    sm = smClass()
    sessionExpireThread = Thread(target=expireSessions, name='Session expriration thread')
    sessionExpireThread.start()
    isActive = True
    _sessionList = []
    
def create(oUser):
    # create new session
    oNewSession = sm.createSession(oUser)
    sm.putSession(oNewSession)
    _sessionList.append(oNewSession.sessionid)
    return(oNewSession)
   
def fetchSession(sessionid):
    session = sm.getSession(sessionid)
    if session:
        # update last access time
        session.keepAlive()
    return(session)
    
def expireSessions():
    from porcupine.core.management import Mgt
    while isActive:
        if not sm.supports_replication or Mgt.mgtServer.isMaster():
            for sessionid in _sessionList:
                oSession = sm.getSession(sessionid)
                if time.time() - oSession.lastAccessed > timeout:
                    logging.getLogger('serverlog').debug('Expiring Session: %s' % sessionid)
                    oSession.terminate()
                    logging.getLogger('serverlog').debug('Total active sessions: %s' % str(len(_sessionList)))
                else:
                    break
        time.sleep(1.0)
    
def close():
    global isActive
    isActive = False
    if sessionExpireThread.isAlive():
        sessionExpireThread.join()
    # remove temporary files
    for sessionid in _sessionList:
        sm.getSession(sessionid).removeTempFiles()
    sm.close()
