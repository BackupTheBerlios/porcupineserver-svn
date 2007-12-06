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
"Porcupine scheduler base classes"
import time
from threading import Thread

from porcupine import serverExceptions
from porcupine.core.services.service import BaseService

class BaseTask(BaseService):
    "Porcupine base class for scheduled task services"
    def __init__(self, name, interval):
        BaseService.__init__(self, name)
        self.interval = interval
        
    def start(self):
        self.thread = Thread(name='%s thread' % self.name,
                             target=self.thread_loop)
        self.running = True
        self.thread.start()
    
    def shutdown(self):
        self.running = False
        self.thread.join()
        
    def thread_loop(self):
        while self.running:
            try:
                self.execute()
            except:
                e = serverExceptions.InternalServerError()
                e.writeToLog()
            time.sleep(self.interval)
            
    def execute(self):
        raise NotImplementedError
        