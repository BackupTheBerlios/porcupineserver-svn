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
"Validates miscelanous server parameters"

from porcupine import serverExceptions
from porcupine.config.settings import settings
from porcupine.utils import misc

# [server] section
try:
    serverAddress = misc.getAddressFromString(settings.server.address)
except AttributeError:
    raise serverExceptions.ConfigurationError, (('address', 'server'),)
except:
    raise serverExceptions.ConfigurationError, 'Invalid server bind address: %s' % settings.server.address

try:
    worker_threads = int(settings.server.worker_threads)
except AttributeError:
    raise serverExceptions.ConfigurationError, (('worker_threads', 'server'),)
except ValueError:
    raise serverExceptions.ConfigurationError, 'Invalid workder_threads setting: %s' % settings.server.worker_threads

try:
    allow_guests = int(settings.server.allow_guests)
except AttributeError:
    raise serverExceptions.ConfigurationError, (('allow_guests', 'server'),)
except ValueError:
    raise serverExceptions.ConfigurationError, 'Invalid allow_guests setting: %s' % settings.server.allow_guests

try:
    temp_folder = settings.server.temp_folder
except AttributeError:
    raise serverExceptions.ConfigurationError, (('temp_folder', 'server'),)

try:
    login_page = settings.server.login_page
except AttributeError:
    raise serverExceptions.ConfigurationError, (('login_page', 'server'),)

# [sessionmanager] section
try:
    guest_account = settings.sessionmanager.guest
except AttributeError:
    raise serverExceptions.ConfigurationError, (('guest', 'sessionmanager'),)
