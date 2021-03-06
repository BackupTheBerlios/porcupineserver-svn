#!/usr/bin/env python
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
"Utility for Porcupine Server database backup"

import getopt
import sys
import socket

from porcupine.utils import misc
from porcupine.core.services import management

__usage__ = """
DATABASE COMMANDS
=================

    Backup database:
        $ python porcupineadmin.py -b -s SERVERNAME:SERVERPORT -f BACKUPFILE or
        $ python porcupineadmin.py --backup --server=SERVERNAME:SERVERPORT --file=BACKUPFILE
        
    Restore database:
        $ python porcupineadmin.py -r -s SERVERNAME:SERVERPORT -f BACKUPFILE or
        $ python porcupineadmin.py --restore --server=SERVERNAME:SERVERPORT --file=BACKUPFILE
        
    Shrink database:
        $ python porcupineadmin.py -h -s SERVERNAME:SERVERPORT or
        $ python porcupineadmin.py --shrink --server=SERVERNAME:SERVERPORT
        
    Recover database:
        $ python porcupineadmin.py -c [-s SERVERNAME:SERVERPORT] or
        $ python porcupineadmin.py --recover [--server=SERVERNAME:SERVERPORT]
    
    SERVERNAME:SERVERPORT - The management server address (i.e. localhost:6001)
    BACKUPFILE - The server's local path to the backup file
"""

def usage():
    print __usage__
    sys.exit(2)

# get arguments
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "brhcs:f:",
                               ["backup","restore","shrink",
                                "recover","server=","file="])
except getopt.GetoptError:
    usage()

command = ''
address = ()
file = ''

if opts:
    for opt, arg in opts:                
        if opt in ('-b', '--backup'):
            command = 'DB_BACKUP'
        elif opt in ('-r', '--restore'):
            command = 'DB_RESTORE'
        elif opt in ('-h', '--shrink'):
            command = 'DB_SHRINK'
        elif opt in ('-c', '--recover'):
            command = 'DB_RECOVER'
        elif opt in ('-s', '--server'):
            address = arg
        elif opt in ('-f', '--file'):
            file = arg
else:
    usage()

if not command or (command != 'DB_RECOVER' and not address):
    usage()
    
try:
    if address:
        address = misc.getAddressFromString(address)
except:
    sys.exit('Invalid server address...')

# construct request object
if command in ('DB_BACKUP', 'DB_RESTORE'):
    if not(file):
        usage()
    msg = management.MgtMessage(command, file)
elif command == 'DB_RECOVER' and not address:
    answer = raw_input('''
WARNING: You are about to perform an offline recovery.
Please ensure that all Porcupine services are stopped,
since database recovery requires a single-threaded environment.

Are you sure you want proceed(Y/N)?''')
    if (answer.upper() == 'Y'):
        try:
            from porcupine.db import _db
            print 'Recovering database...'
            _db._recover()
            _db.close()
            print 'Database recovery completed successfully.'
        except Exception, e:
            sys.exit(e)
    sys.exit()
else:
    msg = management.MgtMessage(command, '')

request = management.MgtRequest(msg.serialize())

try:
    response = request.getResponse(address)
except socket.error:
    sys.exit('The host is unreachable...')

if response.header == 0:
    print response.data
else:
    sys.exit(response.data)
