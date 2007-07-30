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
"Server replication settings"

from porcupine import serverExceptions
from porcupine.config.settings import settings
from porcupine.utils import misc

try:
    host_priority = int(settings.replication.priority)
except AttributeError:
    raise serverExceptions.ConfigurationError, (('priority', 'replication'),)
except ValueError:
    raise serverExceptions.ConfigurationError, 'Invalid replication host priority setting: %s' % settings.replication.priority

try:
    hostaddr = misc.getAddressFromString(settings.replication.host_address)
except ValueError:
    raise serverExceptions.ConfigurationError, 'Invalid host address setting: %s' % settings.replication.host_address
except AttributeError:
    hostaddr = None