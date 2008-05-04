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

import getopt, sys, socket

from porcupine.utils import misc
from porcupine.services import management

__usage__ = """
Backup database:
    db_backup.py -b -s SERVERNAME:SERVERPORT -f BACKUPFILE or
    db_backup.py --backup --server=SERVERNAME:SERVERPORT --file=BACKUPFILE
    
Restore database:
    db_backup.py -r -s SERVERNAME:SERVERPORT -f BACKUPFILE or
    db_backup.py --restore --server=SERVERNAME:SERVERPORT --file=BACKUPFILE
    
Shrink database:
    db_backup.py -h -s SERVERNAME:SERVERPORT or
    db_backup.py --shrink --server=SERVERNAME:SERVERPORT

SERVERNAME:SERVERPORT - The management server address.
BACKUPFILE - The path to the backup file.
"""

def usage():
    print __usage__
    sys.exit(2)

# get arguments
argv = sys.argv[1:]
try:
    opts, args = getopt.getopt(argv, "brhs:f:", ["backup","restore","shrink","server=","file="])
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
        elif opt in ('-s', '--server'):
            address = arg
        elif opt in ('-f', '--file'):
            file = arg
else:
    usage()

if not command or not address:
    usage()

try:
    address = misc.getAddressFromString(address)
except:
    sys.exit('Invalid server address...')

# construct request object
if command in ('DB_BACKUP', 'DB_RESTORE'):
    if not(file):
        usage()
    msg = management.MgtMessage(command, file)
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
