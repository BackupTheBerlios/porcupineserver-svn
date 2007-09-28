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
"Porcupine main service"

from threading import currentThread
from cPickle import loads
from socket import error as socketError

from porcupine.core import request
from porcupine.core.services import asyncBaseServer
from porcupine.services.porcupineThread import PorcupineThread
from porcupine import serverExceptions

class PorcupineServer(asyncBaseServer.BaseServer):
    "Porcupine server class"
    def __init__(self, name, address, threads):
        asyncBaseServer.BaseServer.__init__(self, name,
            address, threads, PorcupineThread, requestHandler)

class requestHandler(asyncBaseServer.BaseRequestHandler):
    "Porcupine Server request handler"
    def handleRequest(self):
        oCurrentThread = currentThread()
        oCurrentThread.request = request.Request(loads(self.input_buffer))
        try:
            oCurrentThread.getResponse()
        except serverExceptions.ProxyRequest:
##            print 'redirecting request'
##            time.sleep(10.0)
            masterAddr = Mgt.mgtServer.siteInfo.getMaster(1)
            oRequest = asyncBaseServer.BaseRequest(self.input_buffer)
            try:
                sResponse = oRequest.getResponse(masterAddr)
                self.write_buffer(sResponse)
            except socketError:
                # the master is down!!!
                # remove master from replication site
                master = Mgt.mgtServer.siteInfo.getMaster()
                Mgt.mgtServer.siteInfo.removeHost(master)
                # I am the new master...
                # re-process the request
                self.handleRequest()