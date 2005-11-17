#!/usr/bin/env python
#===============================================================================
#    Copyright 2005, Tassos Koutsovassilis
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
"Porcupine Server"

import logging, sys, os, time, signal, imp
import warnings, exceptions
from threading import Thread, currentThread, Event
from cPickle import loads
from socket import error as socketError

from porcupine.core import request, asyncBaseServer
from porcupine.core.management import Mgt
from porcupine.db import db
from porcupine.security import sessionManager
from porcupine import serverExceptions
from porcupine.config import serverLogging

warnings.filterwarnings('ignore', '', exceptions.Warning, 'logging')
__version__ = '0.0.5 build(20051117)'
PID_FILE = 'conf/.pid'

class PorcupineServer(asyncBaseServer.BaseServer):
    "Porcupine server class"
    def __init__(self):

        self.running = False
        self.sessionManager = None
        self.mgtServer = None
        logger = serverLogging.logger

        self.shutdownEvt = Event()
        self.shutdownThread = Thread(
            target=self.shutdown,
            name='Shutdown thread'
        )
        self.shutdownThread.start()

        try:
            # initialize logging
            serverLogging.initialize_logging()
            
            logger.info('Server starting...')

            # get server parameters
            from porcupine.config import serverSettings

            # get request interfaces
            from porcupine.config import requesttypes
            logger.info('Succesfullly registered %i request interfaces' % \
                len(requesttypes.requestInterfaces))

            # load registrations
            logger.info('Loading store & web apps registrations...')
            from porcupine.config import registrations

            logger.info('Starting management server...')
            from porcupine.config import mgtparams
            Mgt.open(mgtparams.serverAddress, mgtparams.worker_threads)

            # open database
            logger.info('Opening database...')
            from porcupine.config import dbparams
            db.open(dbparams.db_class)

            # create session manager
            logger.info('Creating session manager...')
            from porcupine.config import smparams
            sessionManager.open(smparams.sm_class, smparams.timeout)

            Mgt.mgtServer.mainServer = self
            
            # replication
            if db.db_handle.supports_replication or \
                    sessionManager.sm.supports_replication:
                from porcupine.config import replication

                # check if we have consistent interfaces
                if db.db_handle.supports_replication != \
                        sessionManager.sm.supports_replication:
                    if db.db_handle.supports_replication and \
                            not(sessionManager.sm.supports_replication):
                        sError = 'Database supports replication but the ' + \
                                    'session manager does not.'
                    else:
                        sError = 'Session manager supports replication but ' + \
                                    'the store does not.'
                    raise serverExceptions.ConfigurationError, \
                        'Mismatched interfaces.\n%s' % sError

                Mgt.mgtServer.sync(replication.host_priority, \
                    replication.hostaddr)

            # start server
            logger.info('Starting main service...')
            from porcupine.core import thread
            asyncBaseServer.BaseServer.__init__(self, "Porcupine Server",
                serverSettings.serverAddress, serverSettings.worker_threads,
                thread.PorcupineThread, requestHandler)

        except serverExceptions.ConfigurationError, e:
            logger.error(e.info)
            self.initiateShutdown()
            raise e

        # record process id
        pidfile = file(PID_FILE, "w")
        pidfile.write(str(os.getpid()))
        pidfile.close()
        
        logger.info('Porcupine Server started succesfully')
        print 'Porcupine Server v%s' % __version__
        print 'Python version is: %s' % sys.version
        print '''Porcupine comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under
certain conditions; See COPYING for more details.'''

    def initiateShutdown(self, arg1=None, arg2=None):
        self.shutdowninprogress = True
        self.shutdownEvt.set()

    def shutdown(self):
        self.shutdownEvt.wait()
        logger = serverLogging.logger
        logger.info('Initiating shutdown...')

        if self.running:
            logger.info('Shutting down main service...')
            asyncBaseServer.BaseServer.shutdown(self)

        # shutdown session manager
        if sessionManager.sm:
            logger.info('Closing session manager...')
            sessionManager.close()
        
        # close database
        if db.db_handle:
            logger.info('Closing database...')
            db.close()

        if Mgt.mgtServer:
            logger.info('Shutting down administation service')
            Mgt.mgtServer.shutdown()

        logger.info('All services have been shut down successfully')
        # shutdown logging
        logging.shutdown()
        self.shutdowninprogress = False

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

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def main(args):
    for arg in args:
        if arg == 'daemon':
            if os.name == 'posix':
                out = file('out', 'w')
                sys.stdout = out
                sys.stderr = out
                pid=os.fork()
                if pid:
                    sys.exit()
            else:
                print 'Your operating system does not support daemon mode.'
        elif arg == 'stop':
            pidfile = open(PID_FILE, 'r')
            pid = int(pidfile.read())
            pidfile.close
            if os.name == 'posix':
                os.kill(pid, signal.SIGINT)
            else:
                print 'Your operating system does not support this command.'
            sys.exit()

    if main_is_frozen():
        sys.path.insert(0, '')

    try:
        server = PorcupineServer()
    except serverExceptions.ConfigurationError, e:
        sys.exit(e.info)

    if (os.name=='nt'):
        try:
            while server.running:
                time.sleep(3.0)
        except KeyboardInterrupt:
            print 'Initiating shutdown...'
            server.initiateShutdown()
    else:
        signal.signal(signal.SIGINT, server.initiateShutdown)
        signal.signal(signal.SIGTERM, server.initiateShutdown)
        while server.running:
            time.sleep(3.0)

    server.shutdownThread.join()
    sys.exit()

if __name__=='__main__':
    main(sys.argv[1:])