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
"Session classes for single server and replicated environments"

import time, tempfile
import os, glob

from porcupine.config.services import services
from porcupine import serverExceptions
from porcupine.security import SessionManager
from porcupine.services import management
from porcupine.utils import misc

class Session(object):
    __slots__ = ('sessionid', 'lastAccessed', '__user', '__data')
    """
    Porcupine server session type.
    
    @ivar sessionid: A unique identifier for the session
    @type sessionid: str
    
    @type user: L{GenericItem<porcupine.systemObjects.GenericItem>}
    """
    def __init__(self, sessionid, oUser, sessiondata):
        self.sessionid = sessionid
        self.lastAccessed = time.time()
        self.__user = oUser
        self.__data = sessiondata

    def keepAlive(self):
        """
        Called by the application server. Updates the session's
        last accessed time, thus the session does not expire.
        
        @return: None
        """
        # move sessionid at the end of the list
        SessionManager._sessionList.append(self.sessionid)
        SessionManager._sessionList.remove(self.sessionid)
        # update last access time
        self.lastAccessed = time.time()

    def terminate(self):
        """
        Kills the session.
        
        @return: None
        """
        SessionManager.sm.removeSession(self.sessionid)
        SessionManager._sessionList.remove(self.sessionid)
        self.removeTempFiles()

    def setValue(self, sName, value):
        """
        Creates or updates a session variable.
        
        @param sName: the name of the variable
        @type sName: str
        
        @param value: the value of the variable.
        @type value: type
        
        @return: None
        """
        self.__data[sName] = value

    def getValue(self, sName):
        """
        Retrieves a session variable.
        
        @param sName: the name of the variable
        @type sName: str

        @rtype: type
        """
        return self.__data.get(sName, None)

    def getTempFile(self):
        """
        Creates a temporary file bound to the session.
        Returns a tuple containing an OS-level handle to an open
        file (as would be returned by os.open()) and the absolute
        pathname of that file, in that order.
        
        @rtype: tuple
        """
        return tempfile.mkstemp(prefix=self.sessionid,
                                dir=services['main'].parameters['temp_folder'])
    
    def getTempFilename(self):
        """
        Returns a temporary file name bound to the session.
                
        @rtype: string
        """
        return  services['main'].parameters['temp_folder'] + \
                '/' + self.sessionid + '_' + \
                misc.generateOID()

    def removeTempFiles(self):
        """
        Removes all the session's temporary files.
        
        @return: None
        """
        tmpFiles = glob.glob(services['main'].parameters['temp_folder'] +
                             '/' + self.sessionid + '*')
        for tmpFile in tmpFiles:
            os.remove(tmpFile)

    def setUser(self, oUser):
        """
        Setter for the L{user} property.
        """
        self.__user = oUser

    def getUser(self):
        """
        Getter of the L{user} property.
        
        @rtype: type
        """
        return(self.__user)
    user = property(getUser, setUser, None, 'The session\'s user')

    def getData(self):
        """
        Returns all the session's variables.
        
        @rtype: dict
        """
        return(self.__data)

class ReplSession(Session):
    """The session type used on replicated environments
    
    @type user: L{GenericItem<porcupine.systemObjects.GenericItem>}
    """
    def keepAlive(self):
        SessionManager.sm.waitForUnlock()
        Session.keepAlive(self)
        services['management'].sendMessage(management.REP_BROADCAST,
                                          'KEEP_ALIVE',
                                          self.sessionid)
    
    def setUser(self, oUser):
        # check if i am the master
        if Mgt.mgtServer.isMaster():
            # wait until sessionmanager is unlocked...
            SessionManager.sm.waitForUnlock()
            Session.setUser(self, oUser)
            services['management'].sendMessage(management.REP_BROADCAST,
                                      'SESSION_USER',
                                      (self.sessionid, oUser._id))
        else:
            raise serverExceptions.ProxyRequest

    user = property(Session.getUser, setUser, None, 'The session\'s user')

    def setValue(self, sName, value):
        # check if i am the master
        if Mgt.mgtServer.isMaster():
            # wait until sessionmanager is unlocked...
            SessionManager.sm.waitForUnlock()
            Session.setValue(self, sName, value)
            services['management'].sendMessage(management.REP_BROADCAST,
                                              'SESSION_VALUE',
                                              (self.sessionid, sName, value))
        else:
            raise serverExceptions.ProxyRequest
