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
"Server session manager handle"

from porcupine.config.settings import settings
from porcupine.utils import misc
from porcupine import serverExceptions

try:
    sm_class = settings.sessionmanager.interface
except AttributeError:
    raise serverExceptions.ConfigurationError, \
        (('interface', 'sessionmanager'),)

try:
    timeout = int(settings.sessionmanager.timeout)
except AttributeError:
    # default timeout set to 20 minutes
    timeout = 1200
except ValueError:
    raise serverExceptions.ConfigurationError, \
        'Invalid value for session manager timeout: %s' % \
        settings.sessionmanager.timeout

try:
    sm_class = misc.getClassByName(sm_class)
except AttributeError:
    raise serverExceptions.ConfigurationError, \
        'Invalid session manager interface "%s"' % \
        settings.sessionmanager.interface
except ImportError:
    raise serverExceptions.ConfigurationError, \
        'Invalid session manager interface "%s"' % \
        settings.sessionmanager.interface
