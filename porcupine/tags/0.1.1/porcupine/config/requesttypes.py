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
"Server request interfaces"

from porcupine.config.settings import settings
from porcupine.utils import misc
from porcupine import serverExceptions

requestInterfaces = {}

try:
    ris = settings.requestinterfaces.options
except AttributeError:
    raise serverExceptions.ConfigurationError, 'The configuration file either has no [requestinterfaces] section or the aforementioned section is blank'

for ri in ris:
    sInterface = getattr(settings.requestinterfaces, ri)
    try:
        requestInterfaces[ri.upper()] = misc.getCallableByName(sInterface)
    except AttributeError:
        raise serverExceptions.ConfigurationError, 'Invalid request interface "%s"' % sInterface
    except ImportError:
        raise serverExceptions.ConfigurationError, 'Invalid request interface "%s"' % sInterface

del ris    
