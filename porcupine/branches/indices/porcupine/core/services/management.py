#===============================================================================
#    Copyright 2005-2008 Tassos Koutsovassilis
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
"Porcupine Server management service"
import logging
from cPickle import dumps, loads

from porcupine.core.servicetypes import asyncserver
from porcupine.core.networking.request import BaseRequest
from porcupine.db import _db

logger = logging.getLogger('serverlog')

class MgtRequest(BaseRequest):
    def get_response(self, addr):
        resp = BaseRequest.get_response(self, addr)
        response = MgtMessage()
        response.load(resp)
        return(response)

class MgtMessage(object):
    """
    Management message exchange class
    """
    def __init__(self, header=None, data=None):
        self.__msg = [header, data]

    def getHeader(self):
        return(self.__msg[0])
    header = property(getHeader)

    def getData(self):
        return(self.__msg[1])
    data = property(getData)

    def load(self, s):
        self.__msg = loads(s)

    def serialize(self):
        s = dumps(self.__msg)
        return(s)

class ManagementServer(asyncserver.BaseServer):
    "Management Service"
    def __init__(self, name, serverAddress, worker_threads):
        asyncserver.BaseServer.__init__(self, name, serverAddress,
            worker_threads, asyncserver.BaseServerThread, ManagementRequestHandler)

    def shutdown(self):
        if self.running:
            asyncserver.BaseServer.shutdown(self)

class ManagementRequestHandler(asyncserver.BaseRequestHandler):
    "Porcupine Server Management request handler"
    def handle_request(self):
        request = MgtMessage()
        request.load(self.input_buffer)   
        cmd = request.header
        
        try:
            args = self.executeCommand(cmd, request)
            if args:
                response = MgtMessage(*args)
                # send the response
                self.write_buffer(response.serialize())
        except:
            logger.log(logging.ERROR, 'Management Error:', *(), **{'exc_info':1})
            error_msg = MgtMessage(-1,
                            'Internal server error. See server log for details.')
            self.write_buffer(error_msg.serialize())

    def executeCommand(self, cmd, request):        
        #DB maintenance commands
        try:
            if cmd=='DB_BACKUP':
                output_file = request.data
                try:
                    _db.lock()
                    backfiles = _db.backup(output_file)
                finally:
                    _db.unlock()
                return (0, 'Database backup completed successfully.')
            
            elif cmd=='DB_RESTORE':
                backup_set = request.data
                _db.restore(backup_set)
                return (0, 'Database restore completed successfully.')
    
            elif cmd=='DB_RECOVER':
                _db.close()
                _db.recover()
                return (0, 'Database recovery completed successfully.')
            
            elif cmd=='DB_SHRINK':
                iLogs = _db.shrink()
                if iLogs:
                    return (0, 'Successfully removed %d log files.' % iLogs)
                else:
                    return (0, 'No log files removed.')
            
            # unknown command
            else:
                logger.warning(
                    'Management service received unknown command: %s' % cmd)
                return (-1, 'Unknown command.')
        except IOError:
            return (-1, 'Invalid file path.')
        except NotImplementedError:
            return (-1, 'Unsupported command.')
