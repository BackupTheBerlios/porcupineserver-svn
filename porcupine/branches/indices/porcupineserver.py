#!/usr/bin/env python
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
"Porcupine Server"

import logging, sys, os, time, signal, imp
import warnings, exceptions
from threading import Thread, Event

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

if main_is_frozen():
    sys.path.insert(0, '')

from porcupine.config import services, log
from porcupine.utils import misc
from porcupine.db import _db
from porcupine.security import SessionManager

warnings.filterwarnings('ignore', '', exceptions.Warning, 'logging')
__version__ = '0.5 build(20080223)'
PID_FILE = 'conf/.pid'

class Controller(object):
    def __init__(self):
        self.shutdowninprogress = False
        self.running = False
        self.logger = logging.getLogger('serverlog')
        self.services = services.services
    
    def start(self):
        try:
            # read configuration file
            from porcupine.config.settings import settings
            # initialize logging
            log.initialize_logging()
            self.logger.info('Server starting...')
            
            # register request interfaces
            for key, value in settings['requestinterfaces'].items():
                settings['requestinterfaces'][key] = \
                    misc.getCallableByName(value)
            self.logger.info('Succesfullly registered %i request interfaces' % \
                             len(settings['requestinterfaces']))
            
            # register template languages
            for key, value in settings['templatelanguages'].items():
                settings['templatelanguages'][key] = \
                    misc.getCallableByName(value)
            self.logger.info('Succesfullly registered %i template languages' % \
                             len(settings['templatelanguages']))
                        
            # load published directories
            self.logger.info('Loading published directories\' registrations...')
            from porcupine.config import pubdirs

            # open database
            self.logger.info('Opening database...')
            _db.open()

            # create session manager
            self.logger.info('Creating session manager...')
            SessionManager.open(misc.getCallableByName(
                            settings['sessionmanager']['interface']),
                            int(settings['sessionmanager']['timeout']))
            
            self.services['_controller'] = self
            # start services
            self.logger.info('Starting services...')
            services.startServices()
            
        except Exception, e:
            self.logger.log(logging.ERROR, e[0], *(), **{'exc_info' : True})
            raise e
        
        # start shutdown thread
        self.shutdownEvt = Event()
        self.shutdownThread = Thread(
            target=self.shutdown,
            name='Shutdown thread'
        )
        self.shutdownThread.start()

        self.running = True

        # record process id
        pidfile = file(PID_FILE, "w")
        pidfile.write( str(os.getpid()) )
        pidfile.close()
        
        self.logger.info('Porcupine Server started succesfully')
        print 'Porcupine Server v%s' % __version__
        sPythonVersion = 'Python %s' % sys.version
        self.logger.info(sPythonVersion)
        print sPythonVersion
        print '''Porcupine comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under
certain conditions; See COPYING for more details.'''

    def initiateShutdown(self, arg1=None, arg2=None):
        self.shutdowninprogress = True
        self.shutdownEvt.set()
        
    def shutdown(self):
        self.shutdownEvt.wait()
        self.logger.info('Initiating shutdown...')

        # stop services
        self.logger.info('Stopping services...')
        for service in [x for x in self.services.values()
                        if x is not self]:
            service.shutdown()

        self.running = False
        
        # shutdown session manager
        if SessionManager.sm:
            self.logger.info('Closing session manager...')
            SessionManager.close()
        
        # close database
        if _db.is_open():
            self.logger.info('Closing database...')
            _db.close()

        self.logger.info('All services have been shut down successfully')
        # shutdown logging
        logging.shutdown()
        self.shutdowninprogress = False

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

    try:
        controller = Controller()
        controller.start()
    except Exception, e:
        sys.exit(e)

    if (os.name=='nt'):
        try:
            while controller.running:
                time.sleep(3.0)
        except KeyboardInterrupt:
            print 'Initiating shutdown...'
            controller.initiateShutdown()
    else:
        signal.signal(signal.SIGINT, controller.initiateShutdown)
        signal.signal(signal.SIGTERM, controller.initiateShutdown)
        while controller.running:
            time.sleep(3.0)

    controller.shutdownThread.join()
    sys.exit()

if __name__=='__main__':
    main(sys.argv[1:])
