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
"Porcupine Server Exception classes"

import logging
import types
from porcupine import errors

class ResponseEnd(Exception):
    pass

class ConfigurationError(Exception):
    def __init__(self, descr):
        if type(descr) == types.StringType:
            self.info = descr
        elif type(descr) == types.TupleType:
            self.info = 'The configuration file is missing option "%s" in section [%s]' % descr

class PorcupineException(Exception):
    def __init__(self, info=''):
        self.code = 0
        self.severity = 0
        self.outputTraceback = False
        self.info = info

    def writeToLog(self):
        if self.severity:
            serverLogger = logging.getLogger('serverlog')
            sDescr = self.description
            if self.info:
                sDescr += '\n%s' % self.info
            if self.outputTraceback:
                serverLogger.log(self.severity, sDescr, *(), **{'exc_info':1})
            else:
                serverLogger.log(self.severity, sDescr)

    def getDescription(self):
        return errors.ERROR_DESCRIPTIONS.setdefault(self.code, 'No description available.')
    
    description = property(getDescription)

# server exceptions

class InternalServerError(PorcupineException):
    def __init__(self, info=''):
        PorcupineException.__init__(self, info)
        self.code = errors.SERVER_INTERNAL_ERROR
        self.severity = logging.ERROR
        self.outputTraceback = True
        
class XMLRPCError(PorcupineException):
    def __init__(self, info=''):
        PorcupineException.__init__(self, info)
        self.code = errors.SERVER_XMLRPC_ERROR
        self.severity = logging.ERROR

class InvalidRegistration(PorcupineException):
    def __init__(self, info=''):
        PorcupineException.__init__(self, info)
        self.code = errors.SERVER_INVALID_REG
        self.severity = logging.ERROR

class NoViewRegistered(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.SERVER_NO_VIEW
        self.severity = logging.WARNING

class ItemNotFound(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.SERVER_NOT_FOUND
        self.severity = logging.WARNING

class PermissionDenied(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.SERVER_NO_ACCESS
        
class PolicyViolation(PorcupineException):
    def __init__(self, info):
        PorcupineException.__init__(self, info)
        self.code = errors.SERVER_POLICY_VIOLATION
        self.severity = logging.WARNING

class OQLError(PorcupineException):
    def __init__(self, info):
        PorcupineException.__init__(self, info)
        self.code = errors.SERVER_OQL_ERROR
        self.severity = logging.ERROR

# database exceptions

class DBItemAlreadyExists(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_ITEM_ALREADY_EXISTS
        self.severity = logging.WARNING

class TargetContainedInSource(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_INVALID_MOVE
        self.severity = logging.WARNING

class TransactionRequired(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_TRANS_REQUIRED
        self.severity = logging.WARNING

class DBItemNotFound(PorcupineException):
    def __init__(self, info=''):
        PorcupineException.__init__(self, info)
        self.code = errors.DB_ITEM_NOT_FOUND
        self.severity = logging.WARNING

class DBTransactionIncomplete(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_TRANS_INCOMPLETE
        self.severity = logging.CRITICAL

class ContainmentError(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_CONTAINMENT_ERROR
        self.severity = logging.WARNING

class ReferentialIntegrityError(PorcupineException):
    def __init__(self):
        PorcupineException.__init__(self)
        self.code = errors.DB_REFERENCE_ERROR
        self.severity = logging.WARNING

class ValidationError(PorcupineException):
    def __init__(self, info=''):
        PorcupineException.__init__(self, info)
        self.code = errors.DB_VALIDATION_ERROR
        self.severity = logging.WARNING

# replication exceptions

class ProxyRequest(Exception):
    pass

class HostUnreachable(Exception):
    pass

class ReplicationError(PorcupineException):
    def __init__(self, code):
        PorcupineException.__init__(self)
        self.code = code

        
