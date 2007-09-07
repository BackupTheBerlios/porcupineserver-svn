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
"Porcupine configured services loader"

from porcupine.config.settings import settings
from porcupine.utils import misc

services = {}

def startServices():
    for service in settings['services']:
        name = service['name']
        type = service['type']
        service_class = misc.getCallableByName(service['class'])
        if type == 'TCPListener':
            services[name] = service_class(name,
                                       misc.getAddressFromString(service['address']),
                                       service['worker_threads'])
        # add parameters
        if service.has_key('parameters'):
            services[name].parameters = service['parameters']