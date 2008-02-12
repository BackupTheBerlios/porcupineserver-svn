#===============================================================================
#    Copyright 2005-2007 Tassos Koutsovassilis
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
"Porcupine Server management service"

import logging, socket
from threading import Thread
from cPickle import dumps, loads, PicklingError

from porcupine.config.services import services
from porcupine.core.services import asyncBaseServer
from porcupine import serverExceptions, errors
from porcupine.db import db
from porcupine.security import SessionManager

logger = logging.getLogger('serverlog')

REP_BROADCAST = -1
REP_COMMANDS = (
	'REPL_DATA','TRANS_DATA',
	'NEW_SESSION','DEL_SESSION',
	'KEEP_ALIVE','SESSION_USER',
	'SESSION_VALUE'
)
MAX_HOSTS = 2

class Site(object):
    "Site info class"
    def __init__(self, replicator):
        self.__info = []
        self.replicator = replicator

    def addHost(self, address, priority, server_address):
        iIndex = 0
        for host in self.__info:
            if priority > host[1]:
                break
            iIndex += 1
        self.__info.insert(iIndex, (address, priority, server_address))
        # we need to broadcast new site info
        self.replicator.sendMessage(REP_BROADCAST, 'SITE_INFO', self.__info)
        self.logMaster()

    def removeHost(self, address):
        for host in self.__info:
            if address == host[0]:
                self.__info.remove(host)
                if self.__info:
                    sError = 'Host %s:%d is down!' % (host[2][0], host[2][1])
                    print sError
                    logger.critical(sError)
                    self.logMaster()
                    # we need to broadcast new site info
                    self.replicator.sendMessage(REP_BROADCAST, 'SITE_INFO', self.__info)

    def getMaster(self, addresstype=0):
        if self.__info:
            return self.__info[0][addresstype*2]
        return None

    def logMaster(self):
        master = self.getMaster(1)
        sInfo = 'New master is %s:%d' % (master[0], master[1])
        print sInfo
        logger.info(sInfo)

    def getHosts(self):
        hosts = []
        for host in self.__info:
            hosts.append(host[0])
        return(hosts)

    def getNumOfHosts(self):
        return(len(self.__info))

    def setInfo(self, info):
        self.__info = info
        self.logMaster()

class MgtRequest(asyncBaseServer.BaseRequest):
    def getResponse(self, addr):
        resp = asyncBaseServer.BaseRequest.getResponse(self, addr)
        response = MgtMessage()
        response.load(resp)
        return(response)

class MgtMessage(object):
    """
    Management message exchange class
    """
    def __init__(self, header=None, data=None):
        self.__msg = [header, data]

    def getHeader(self):
        return(self.__msg[0])
    header = property(getHeader)

    def getData(self):
        return(self.__msg[1])
    data = property(getData)

    def load(self, s):
        self.__msg = loads(s)

    def serialize(self):
        s = dumps(self.__msg)
        return(s)

class ManagementServer(asyncBaseServer.BaseServer):
    "Management Service"
    def __init__(self, name, serverAddress, worker_threads):
        self.has_join = False

        asyncBaseServer.BaseServer.__init__(self, name, serverAddress,
            worker_threads, asyncBaseServer.BaseServerThread, ManagementRequestHandler)
            
        self.siteInfo = Site(self)
        self.lastUpdate = 0

    def sync(self, host_priority, hostaddr):
        if hostaddr:
            logger.info('Initiating store replication with master')

            try:            
                response = self.sendMessage(hostaddr, 'GET_MASTER')
            except serverExceptions.ReplicationError, e:
                raise serverExceptions.ConfigurationError, e.description

            masteraddr = response.data
            
            # remove all objects
            db.db_handle._truncate()
            
            # and start replication with master
            try:
                response = self.sendMessage(masteraddr, 'REPL_START',
										    (self.addr, host_priority, services['main'].addr))
            except serverExceptions.ReplicationError, e:
                raise serverExceptions.ConfigurationError, e.description

            logger.info('Store replication completed successfully')
        else:
            logger.info('This node is initially configured as MASTER')
            self.siteInfo.addHost(self.addr, host_priority, services['main'].addr)

        self.has_join = True

    def isMaster(self):
        return(self.addr == self.siteInfo.getMaster())

    def sendMessage(self, address, header, data=None):
        "This is used only for replication commands..."
        msg = MgtMessage(header, data)
        request = MgtRequest(msg.serialize())
        
        if address != REP_BROADCAST:
            try:
                resp = request.getResponse(address)
                if resp.header != 0:
                    if resp.header == errors.MGT_ERROR:
                        # the host did not execute the command correctly
                        # it must be out of site
                        self.siteInfo.removeHost(address)
                    raise serverExceptions.ReplicationError, resp.header
                return(resp)

            except socket.error, e:
                self.siteInfo.removeHost(address)
                raise e

        else:
            # TODO: if we broadcast do we raise exceptions????
            hosts = self.siteInfo.getHosts()
            for host in hosts:
                # ommit myself
                if host != self.addr:
                    try:
                        resp = request.getResponse(host)
                        if resp.header == errors.MGT_ERROR:
                            # the host did not execute the command correctly
                            # it must be out of site
                            self.siteInfo.removeHost(address)

                    except socket.error:
                        self.siteInfo.removeHost(host)


    def shutdown(self):
        # disjoin site
        if self.has_join:
            logger.info('Leaving the replication site...')
            try:
                self.sendMessage(self.siteInfo.getMaster(), 'DISJOIN', self.addr)
            except socket.error:
                # the master is down...
                pass
        if self.running:
            #logger.info('Shutting down management service...')
            asyncBaseServer.BaseServer.shutdown(self)

class ManagementRequestHandler(asyncBaseServer.BaseRequestHandler):
    "Porcupine Server Management request handler"
    def handleRequest(self):
        request = MgtMessage()
        request.load(self.input_buffer)   
        cmd = request.header
        
        try:
            args = self.executeCommand(cmd, request)
            if args:
                response = MgtMessage(*args)
                # send the response
                self.write_buffer(response.serialize())
        except:
            logger.log(logging.ERROR, 'Management Error:', *(), **{'exc_info':1})
            self.write_buffer(MgtMessage(errors.MGT_ERROR).serialize())
            # if the command was a replication command
            # then the server is out of sync
            # we must shutdown
            if cmd in REP_COMMANDS:
                services['_controller'].initiateShutdown()

    def executeCommand(self, cmd, request):        
        # site related commands
        if cmd=='DISJOIN':
            if self.server.isMaster():
                host = request.data
                self.server.siteInfo.removeHost(host)
                return (0,)
            else:
                return (errors.REPL_NO_MASTER,)
        
        elif cmd=='GET_MASTER':
            masteraddr = self.server.siteInfo.getMaster()
            if masteraddr:
                return (0, masteraddr)
            else:
                return (errors.REPL_NOT_SUPP,)

        elif cmd=='SITE_INFO':
            self.server.siteInfo.setInfo(request.data)
            return (0,)
        
        # db update commands
        elif cmd=='TRANS_DATA':
            data = request.data[1]
            trans = db.db_handle.transaction()
            trans.repl_commit(data)
            self.server.lastUpdate = request.data[0]
            return (0,)
            
        # session manager commands
        elif cmd=='NEW_SESSION':
            sessionid, userid, sessiondata = request.data
            SessionManager.sm.repl_addSession(sessionid, userid, sessiondata)
            return (0,)

        elif cmd=='DEL_SESSION':
            SessionManager.sm.repl_removeSession(request.data)
            return (0,)

        elif cmd=='KEEP_ALIVE':
            SessionManager.sm.repl_keepAlive(request.data)
            return (0,)

        elif cmd=='SESSION_USER':
            sessionid, userid = request.data
            SessionManager.sm.repl_setUser(sessionid, userid)
            return (0,)

        elif cmd=='SESSION_VALUE':
            sessionid, name, value = request.data
            SessionManager.sm.repl_setValue(sessionid, name, value)
            return (0,)

        #DB maintenance commands
        elif cmd=='DB_BACKUP':
            output_file = request.data
            try:
                db.lock()
                try:
                    backfiles = db.db_handle._backup(output_file)
                except IOError:
                    return(errors.MGT_INV_FOLDER,)
                except NotImplementedError:
                    return(errors.MGT_NOT_IMPLEMENTED,)
            finally:
                db.unlock()
            return((0,'Database backup completed successfuly.'))
        
        elif cmd=='DB_RESTORE':
            if self.server.siteInfo.getNumOfHosts() < 2:
                backup_set = request.data
                try:
                    db.db_handle._restore(backup_set)
                    return((0,'Database restore completed successfully.'))
                except IOError:
                    return(errors.MGT_INV_FILE,)
                except NotImplementedError:
                    return(errors.MGT_NOT_IMPLEMENTED,)
            else:
                return(errors.MGT_CANNOT_RESTORE,)
        
        elif cmd=='DB_SHRINK':
            try:
                iLogs = db.db_handle._shrink()
                if iLogs:
                    return((0,'Successfully removed %d log files.' % iLogs))
                else:
                    return((0,'No log files removed.'))
            except NotImplementedError:
                return(errors.MGT_NOT_IMPLEMENTED,)

        #DB replication commands
        elif cmd=='REPL_START':
            if self.server.isMaster():
                if self.server.siteInfo.getNumOfHosts() == MAX_HOSTS:
                    return (errors.REPL_SITE_FULL,)
                else:
                    host, host_priority, serverAddress = request.data
                    logger.info('Initiating replication process for host %s:%d' % (host[0], host[1]))
                    
                    try:
                        db.lock()
                        # replicate store
                        all_items = db.db_handle.enumerate()
                        for rec in all_items:
                            try:
                                repl_response = self.server.sendMessage(host, 'REPL_DATA', rec)
                            except socket.error:
                                return
                            except serverExceptions.ReplicationError:
                                return (errors.REPL_ABORT,)
                        
                        SessionManager.sm.lock()
                        # replicate active sessions
                        all_sessions = SessionManager.sm.enumerate()
                        for sessionData in all_sessions:
                            try:
                                repl_response = self.server.sendMessage(host, 'NEW_SESSION', sessionData)
                                
                            except PicklingError:
                                return (errors.REPL_INVALID_SESSION,)
                            except TypeError:
                                return (errors.REPL_INVALID_SESSION,)
                            except socket.error:
                                return
                            except serverExceptions.ReplicationError:
                                return (errors.REPL_ABORT,)

                        # update site info
                        self.server.siteInfo.addHost(host, host_priority, serverAddress)
                    finally:
                        SessionManager.sm.unlock()
                        db.unlock()
                    
                    return (0,)
            else:
                return (errors.REPL_NO_MASTER,)

        elif cmd=='REPL_DATA':
            trans = db.db_handle.transaction()
            targetdb, rec = request.data
            data = {0:{}, 1:{}}
            data[targetdb][rec[0]] = rec[1]
            trans.repl_commit(data)
            return (0,)

        # unknown command
        else:
            logger.warning('Management service received unknown command: %s' % cmd)
            return (errors.MGT_UNKNOWN_COMMAND,)

