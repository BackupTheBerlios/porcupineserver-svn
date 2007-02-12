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
"Server logging initialization module"

import logging
import logging.handlers
from porcupine import serverExceptions
from porcupine.config.settings import settings

logger = logging.getLogger('serverlog')

def initialize_logging():
    try:
        logmaxbytes = int(settings.log.maxbytes)
    except AttributeError:
        raise serverExceptions.ConfigurationError, (('maxbytes', 'log'),)
    except ValueError:
        raise serverExceptions.ConfigurationError, 'Invalid log maxbytes setting: %s' % settings.log.maxbytes

    try:
        logbackups = int(settings.log.backups)
    except AttributeError:
        raise serverExceptions.ConfigurationError, (('backups', 'log'),)
    except ValueError:
        raise serverExceptions.ConfigurationError, 'Invalid log backups setting: %s' % settings.log.backups

    try:
        logformat = settings.log.format
    except AttributeError:
        raise serverExceptions.ConfigurationError, (('format', 'log'),)

    try:
        level = int(settings.log.level)
    except AttributeError:
        raise serverExceptions.ConfigurationError, (('level', 'log'),)
    except ValueError:
        raise serverExceptions.ConfigurationError, 'Invalid log level setting: %s' % settings.log.level

    loghandler = logging.handlers.RotatingFileHandler('log/server.log', 'a', logmaxbytes, logbackups)
    logformatter = logging.Formatter(logformat)
    loghandler.setFormatter(logformatter)
    logger.addHandler(loghandler)
    logger.setLevel(level)
