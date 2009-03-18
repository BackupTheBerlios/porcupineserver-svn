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
"Porcupine service base class"
from porcupine.core import runtime

class BaseService(object):
    runtime_services = []
    def __init__(self, name):
        self.name = name
        self.parameters = None
        self.running = False
        self.started_services = []
        
    def start(self):
        for service, args, kwargs in self.runtime_services:
            inited = getattr(self, 'init_' + service)(*args, **kwargs)
            if inited:
                self.started_services.append(service)
    
    def shutdown(self):
        self.started_services.reverse()
        for service in self.started_services:
            getattr(self, 'close_' +  service)()

    def init_db(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Opening database...' % self.name)
        return runtime.init_db(*args, **kwargs)

    def init_session_manager(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Opening session manager...' %
                            self.name)
        return runtime.init_session_manager(*args, **kwargs)

    def init_config(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Loading configuration...' %
                            self.name)
        runtime.init_config(*args, **kwargs)

    def close_db(self):
        runtime.close_db()

    def close_session_manager(self):
        runtime.close_session_manager()
