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
    def __init__(self, name):
        self.name = name
        self.parameters = None
        self.running = False
        
    def start(self):
        raise NotImplementedError
    
    def shutdown(self):
        raise NotImplementedError

    def init_db(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Opening database...' % self.name)
        runtime.init_db(*args, **kwargs)

    def init_session_manager(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Opening session manager...' %
                            self.name)
        runtime.init_session_manager(*args, **kwargs)

    def init_config(self, *args, **kwargs):
        runtime.logger.info('Service "%s" - Loading configuration...' %
                            self.name)
        runtime.init_config(*args, **kwargs)
