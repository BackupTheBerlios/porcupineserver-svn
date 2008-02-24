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
"Server logging initialization module"

import logging
import logging.handlers
from porcupine.config.settings import settings

def initialize_logging():
    logger = logging.getLogger('serverlog')
    logmaxbytes = int(settings['log']['maxbytes'])
    logbackups = int(settings['log']['backups'])
    logformat = settings['log']['format']
    level = int(settings['log']['level'])

    loghandler = logging.handlers.RotatingFileHandler('log/server.log',
                                                      'a', logmaxbytes,
                                                      logbackups)
    logformatter = logging.Formatter(logformat)
    loghandler.setFormatter(logformatter)
    logger.addHandler(loghandler)
    logger.setLevel(level)
