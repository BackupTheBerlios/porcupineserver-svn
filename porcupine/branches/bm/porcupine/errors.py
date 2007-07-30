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
"Porcupine Server Error Codes & Descriptions"

ERROR_DESCRIPTIONS = {
    4000:'Internal Server Error.',
    4001:'Invalid registration. Could not locate action file.',
    4002:'No registered view for the provided parameters.',
    4004:'Not Found.',
    4005:'Permission Denied.',
    4006:'OQL Error',
    4007:'XML-RPC Error',
    4008:'Policy violation',

    5010:'Cannot create item. Item with the specified name already exists.',
    5011:'Cannot move or copy item to destination. Destination is contained in source.',
    5012:'This action requires transactional context.',
    5013:'Exceeded maximum retries for transcation.',
    5014:'This container does not accept objects of this type.',
    5015:'This item cannot be deleted because it is referenced by other items.',
    5016:'Validation Error.',
    5041:'Object does not exist.',
    
    7000:'Internal management server error. See server log for details.',
    7001:'Not implemented.',
    7002:'Unknown command.',
    7003:'The specified file does not exist.',
    7004:'The specified folder doer not exist.',
    7005:'''Current site configuration includes more than one server.
Disjoin all other servers from the site, then restore, and re-join them again.''',

    8001:'Replication site is full. No more hosts are allowed to join.',
    8003:'Command not sent to master.',
    8004:'Session value contains unpickleable object.',
    8005:'Store replication is aborted due to internal replication server error.',
    8006:'Host does not support replication.'
}

# server configuration errors
SERVER_INTERNAL_ERROR = 4000
SERVER_INVALID_REG = 4001
SERVER_NO_VIEW = 4002
SERVER_NOT_FOUND = 4004
SERVER_NO_ACCESS = 4005
SERVER_OQL_ERROR = 4006
SERVER_XMLRPC_ERROR = 4007
SERVER_POLICY_VIOLATION = 4008

# database error codes
DB_ITEM_ALREADY_EXISTS = 5010
DB_INVALID_MOVE = 5011
DB_TRANS_REQUIRED = 5012
DB_TRANS_INCOMPLETE = 5013
DB_CONTAINMENT_ERROR = 5014
DB_REFERENCE_ERROR = 5015
DB_VALIDATION_ERROR = 5016
DB_ITEM_NOT_FOUND = 5041

# management server error codes
MGT_ERROR = 7000
MGT_NOT_IMPLEMENTED = 7001
MGT_UNKNOWN_COMMAND = 7002
MGT_INV_FILE = 7003
MGT_INV_FOLDER = 7004
MGT_CANNOT_RESTORE = 7005

# replication error codes
REPL_SITE_FULL = 8001
REPL_NO_MASTER = 8003
REPL_INVALID_SESSION = 8004
REPL_ABORT = 8005
REPL_NOT_SUPP = 8006
