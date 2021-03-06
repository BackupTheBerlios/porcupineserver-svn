#==============================================================================
#   Copyright (c) 2005-2010, Tassos Koutsovassilis
#
#   This file is part of Porcupine.
#   Porcupine is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Lesser General Public License as published by
#   the Free Software Foundation; either version 2.1 of the License, or
#   (at your option) any later version.
#   Porcupine is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Lesser General Public License for more details.
#   You should have received a copy of the GNU Lesser General Public License
#   along with Porcupine; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#==============================================================================
"""
Porcupine cookie based session manager classes
"""
import time

from porcupine import context, exceptions
from porcupine.utils import misc
from porcupine.core import persist
from porcupine.core.session.genericsessionmanager import GenericSessionManager
from porcupine.core.session.genericsession import GenericSession


class SessionManager(GenericSessionManager):
    """
    Cookie based session manager implementation class
    """
    supports_multiple_processes = True
    requires_cookies = True

    def __init__(self, timeout, **kwargs):
        GenericSessionManager.__init__(self, timeout)
        secret = kwargs.get('secret', None)
        if not secret:
            raise exceptions.ConfigurationError(
                'The cookie based session manager '
                'should define a secret phrase.')
        Session.secret = secret

    def init_expiration_mechanism(self):
        pass

    def create_session(self, userid):
        session = Session(userid, {})
        session._update()
        return session

    def get_session(self, sessionid):
        request = context.request
        return Session.load(request)

    def remove_session(self, sessionid):
        request = context.request
        response = context.response
        i = 0
        response.cookies['_sid'] = ''
        response.cookies['_sid'] = \
                context.request.serverVariables['SCRIPT_NAME'] + '/'
        session = request.cookies.get('_s%d' % i, None)
        while session is not None:
            response.cookies['_s%d' % i] = ''
            response.cookies['_s%d' % i]['path'] = \
                context.request.serverVariables['SCRIPT_NAME'] + '/'
            i += 1
            session = request.cookies.get('_s%d' % i, None)

    def revive_session(self, session):
        pass

    def close(self):
        pass


class Session(GenericSession):
    """
    Session class for the cookie based session manager
    """
    secret = None

    def __init__(self, userid, sessiondata):
        GenericSession.__init__(self, misc.generate_oid(), userid)
        self.sig = self._get_sig()
        self.__userid = userid
        self.__data = sessiondata

    @staticmethod
    def generate_sig(session):
        return misc.hash(session.sessionid,
                         session.userid,
                         Session.secret,
                         algo='sha256').hexdigest()

    @staticmethod
    def load(request):
        i = 0
        chunks = []
        session = request.cookies.get('_s%d' % i, None)
        while session is not None and session.value:
            chunks.append(session.value)
            i += 1
            session = request.cookies.get('_s%d' % i, None)
        if chunks:
            session = persist.loads(''.join(chunks))
            sig = Session.generate_sig(session)
            if session.sig != sig:
                session = None
        else:
            session = None
        return session

    def _get_sig(self):
        return Session.generate_sig(self)

    def _update(self):
        chunk = persist.dumps(self)
        if type(chunk) != str:
            # python 3: conver to str
            chunk = chunk.decode('latin-1')
        chunks = [chunk[i:i + 4000]
                  for i in range(0, len(chunk), 4000)]
        for i in range(len(chunks)):
            context.response.cookies['_s%d' % i] = chunks[i]
            context.response.cookies['_s%d' % i]['path'] = \
                context.request.serverVariables['SCRIPT_NAME'] + '/'
        j = len(chunks)
        next = context.request.cookies.get('_s%d' % j, None)
        while next:
            context.response.cookies['_s%d' % j] = ''
            context.response.cookies['_s%d' % j]['path'] = \
                context.request.serverVariables['SCRIPT_NAME'] + '/'
            j += 1
            next = context.request.cookies.get('_s%d' % j, None)

    def get_userid(self):
        return self.__userid

    def set_userid(self, value):
        self.__userid = value
        self.sig = self._get_sig()
        self._update()
    userid = property(get_userid, set_userid)

    def set_value(self, name, value):
        self.__data[name] = value
        self._update()

    def get_value(self, name):
        return self.__data.get(name, None)

    def remove_value(self, name):
        del self.__data[name]
        self._update()

    def get_data(self):
        return(self.__data)

    def get_last_accessed(self):
        return time.time()
