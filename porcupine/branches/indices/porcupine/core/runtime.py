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
"""
Porcupine runtime services accessed by multiple processes
"""
import logging
import logging.handlers
try:
    import multiprocessing
except ImportError:
    multiprocessing = None

from porcupine.utils import misc
from porcupine.config.settings import settings

if multiprocessing:
    logger = multiprocessing.get_logger()
else:
    logger = logging.getLogger('serverlog')
_loghandler = logging.handlers.RotatingFileHandler(
    'log/server.log', 'a',
    int(settings['log']['maxbytes']),
    int(settings['log']['backups'])
)
if multiprocessing:
    _loghandler.setFormatter(logging.Formatter(settings['log']['mp_format']))
else:
    _loghandler.setFormatter(logging.Formatter(settings['log']['format']))

logger.addHandler(_loghandler)
logger.setLevel(int(settings['log']['level']))

def init_db(init_maintenance=True):
    from porcupine.db import _db
    if not _db.is_open():
        _db.open(**{'maintain':init_maintenance})

def init_session_manager(init_expiration=True):
    from porcupine.core.session import SessionManager
    SessionManager.open(
        misc.getCallableByName(settings['sessionmanager']['interface']),
        int(settings['sessionmanager']['timeout']),
        init_expiration
    )

def init_config():
    # register request interfaces
    for key, value in settings['requestinterfaces'].items():
        settings['requestinterfaces'][key] = misc.getCallableByName(value)
    # register template languages
    for key, value in settings['templatelanguages'].items():
        settings['templatelanguages'][key] = misc.getCallableByName(value)
    # load published directories
    from porcupine.config import pubdirs

def shutdown():
    from porcupine.db import _db
    from porcupine.core.session import SessionManager
    
    logger.info('Shutting down runtime services...')
    # close session manager
    SessionManager.close()
    # close database
    _db.close()
