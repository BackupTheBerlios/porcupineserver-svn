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
import sys
import os
import time
import signal
import imp
import warnings
import select
from errno import EINTR
from threading import Thread, Event

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

if main_is_frozen():
    sys.path.insert(0, '')

from porcupine.config import services
from porcupine.core import asyncore
from porcupine.core import runtime

warnings.filterwarnings('ignore', '', Warning, 'logging')
__version__ = '0.5.2 build(20081010)'
PID_FILE = 'conf/.pid'

class Controller(object):
    def __init__(self):
        self.shutdowninprogress = False
        self.running = False
        self.services = services.services
    
    def start(self):
        try:
            runtime.logger.info('Server starting...')
            self.services['_controller'] = self
            # start services
            runtime.logger.info('Starting services...')
            services.startServices()
        except Exception, e:
            runtime.logger.error(e[0], *(), **{'exc_info' : True})
            runtime.shutdown()
            raise e

        # start asyn thread
        self._asyn_thread = Thread(target=self._async_loop,
                                   name='Asyncore thread')
        self._asyn_thread.start()
        
        # start shutdown thread
        self.shutdown_evt = Event()
        self.shutdown_thread = Thread(
            target=self.shutdown,
            name='Shutdown thread'
        )
        self.shutdown_thread.start()

        self.running = True

        # record process id
        pidfile = file(PID_FILE, "w")
        pidfile.write(str(os.getpid()))
        pidfile.close()
        
        runtime.logger.info('Porcupine Server started succesfully')
        print 'Porcupine Server v%s' % __version__
        python_version = 'Python %s' % sys.version
        runtime.logger.info(python_version)
        print python_version
        print '''Porcupine comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it under
certain conditions; See COPYING for more details.'''

    def _async_loop(self):
        _use_poll = False
        if hasattr(select, 'poll'):
            _use_poll = True
        try:
            asyncore.loop(30.0, _use_poll)
        except select.error, v:
            if v[0] == EINTR:
                print 'Shutdown not completely clean...'
            else:
                pass

    def initiateShutdown(self, arg1=None, arg2=None):
        self.shutdowninprogress = True
        self.shutdown_evt.set()
        
    def shutdown(self):
        self.shutdown_evt.wait()
        print 'Initiating shutdown...'
        runtime.logger.info('Initiating shutdown...')

        # stop services
        runtime.logger.info('Stopping services...')
        for service in [x for x in self.services.values()
                        if x is not self]:
            service.shutdown()

        self.running = False

        runtime.shutdown()

        # join asyn thread
        asyncore.close_all()
        self._asyn_thread.join()

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

    signal.signal(signal.SIGINT, controller.initiateShutdown)
    signal.signal(signal.SIGTERM, controller.initiateShutdown)

    try:
        while controller.running:
            time.sleep(30.0)
    except IOError:
        pass

    controller.shutdown_thread.join()
    sys.exit()

if __name__=='__main__':
    main(sys.argv[1:])
