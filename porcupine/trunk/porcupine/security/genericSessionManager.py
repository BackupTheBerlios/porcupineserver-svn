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
Generic Session Manager class.
Use this as a base class in order to implement
your own session manager.
"""
from porcupine.security.session import Session
from porcupine.utils import misc

class GenericSessionManager(object):
    sessionClass = Session
    
    def createSession(self, userid):
        session = self.sessionClass(misc.generateGUID(), userid, {})
        return session

    # to be implemented by subclass
    def getSession(self, sessionid):
        raise NotImplementedError

    def putSession(self, session):
        raise NotImplementedError

    def removeSession(self, sessionid):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
