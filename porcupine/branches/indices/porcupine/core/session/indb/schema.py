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
Porcupine database session manager content classes
"""
import time

from porcupine import db
from porcupine import exceptions
from porcupine.systemObjects import Container, GenericItem
from porcupine.core.session.genericsession import GenericSession

class SessionsContainer(Container):
    """
    Container used for keeping active sessions
    """
    containment = ('porcupine.core.session.indb.schema.Session', )

class Session(GenericItem, GenericSession):
    """
    Session object
    """
    def __init__(self, userid, sessiondata):
        GenericItem.__init__(self)
        self.displayName.value = self._id
        self.__data = sessiondata
        self.__userid = userid

    @db.transactional(auto_commit=True)
    def setValue(self, name, value):
        self.__data[name] = value
        trans = db.getTransaction()
        self.update(trans)

    def getValue(self, name):
        return self.__data.get(name, None)
    
    def get_data(self):
        return(self.__data)

    def get_userid(self):
        return self.__userid

    @db.transactional(auto_commit=True)
    def set_userid(self, value):
        self.__userid = value
        trans = db.getTransaction()
        self.update(trans)
    userid = property(get_userid, set_userid)

    def get_sessionid(self):
        return self._id
    sessionid = property(get_sessionid)

    def appendTo(self, parent, trans):
        """
        A lighter appendTo
        """
        if type(parent) == str:
            parent = db._db.getItem(parent, trans)
        
        if not(self.getContentclass() in parent.containment):
            raise exceptions.ContainmentError, \
                'The target container does not accept ' + \
                'objects of type\n"%s".' % contentclass
        
        self._owner = 'system'
        self._created = time.time()
        self.modifiedBy = 'SYSTEM'
        self.modified = time.time()
        self._parentid = parent._id
        db._db.putItem(self, trans)

    def update(self, trans):
        """
        A lighter update
        """
        self.modified = time.time()
        db._db.putItem(self, trans)

    def delete(self, trans):
        """
        A lighter delete
        """
        db._db.deleteItem(self, trans)

    def get_last_accessed(self):
        return self.modified
