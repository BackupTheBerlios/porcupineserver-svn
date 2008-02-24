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
"Porcupine base classes for threaded TCP server"
import socket
import select
import Queue
import time
from threading import Thread, currentThread, RLock
from errno import EINTR, EISCONN, EADDRINUSE

from porcupine.core.services import asyncore
from porcupine.core.services.service import BaseService

USE_POLL = False
if hasattr(select, 'poll'):
    USE_POLL = True

SERVERS = 0
# port range to use when the ephemeral port range is exhausted
PORT_RANGE = range(65535, 49150, -1)
SERVER_IP = socket.gethostbyname(socket.gethostname())
HOST_PORTS = {}
NEXT_PORT_LOCK = RLock()

def nextPort(address):
    NEXT_PORT_LOCK.acquire()
    nextPortIndex = HOST_PORTS[address] = (
        HOST_PORTS.setdefault(address, -1) + 1) % len(PORT_RANGE
    )
    NEXT_PORT_LOCK.release()
    return PORT_RANGE[nextPortIndex]

def asyncLoop():
    try:
        asyncore.loop(0.01, USE_POLL)
    except select.error, v:
        if v[0] == EINTR:
            print "Shutdown not completely clean..."
        else:
            pass

ASYNCORE_THREAD = Thread(target=asyncLoop, name='Asyncore thread')

class BaseServerThread(Thread):
    def __init__(self, target, name):
        Thread.__init__(self, None, target, name)
        self.requestHandler = None

class BaseServer(BaseService, asyncore.dispatcher):
    "Base class for threaded TCP server using asynchronous sockets"
    def __init__(self, name, address, worker_threads, threadClass,
                 requestHandler):
        # initialize base service
        BaseService.__init__(self, name)
        self.addr = address
        self.worker_threads = worker_threads
        self.requestHandler = requestHandler
        self.threadClass = threadClass
        # create client request queue
        self.requestQueue = Queue.Queue(worker_threads*5)
        # create queue for inactive requestHandler objects i.e. those served
        self.rhQueue = Queue.Queue(0)
        # create threads tuple
        self.threadPool = []

    def start(self):
        # activate socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.bind(self.addr)
        except socket.error, v:
            self.close()
            raise v

        self.listen(32)

        for i in range(self.worker_threads):
            tname = '%s server thread %d' % (self.name, i+1)
            t = self.threadClass(target=self.threadLoop, name=tname)
            t.start()
            self.threadPool.append(t)

        self.activeConnections = 0

        global SERVERS
        SERVERS += 1
        # if it is the first server start asyncore loop
        if SERVERS==1:
            ASYNCORE_THREAD.start()
        
        self.running = True

    def readable(self):
        return self.accepting

    def writable(self):
        return False

    def handle_connect(self):
        pass

    def handle_close(self):
        pass

    def handle_accept(self):
        # accept client connection
        clientSocket, addr = self.accept()
        try:
            # get inactive requestHandler from queue
            rh = self.rhQueue.get_nowait()
        except Queue.Empty:
            # if empty then create new requestHandler
            rh = self.requestHandler(self)
        # set the client socket of requestHandler
        self.activeConnections += 1
        clientSocket.setblocking(0)
        rh.activate(clientSocket)

    def threadLoop(self):
        "loop for threads serving content to clients"
        oThread = currentThread()
        while True:
            try:
                # get next waiting client request
                oThread.requestHandler = self.requestQueue.get()
                if oThread.requestHandler == None:
                    break
                else:
                    if oThread.requestHandler.input_buffer:
                        oThread.requestHandler.handleRequest()
                        oThread.requestHandler.hasResponse = True
                    else:
                        # we have a dead socket
                        oThread.requestHandler.close()
            except Queue.Empty:
                pass

    def shutdown(self):
        self.running = False

        self.close()
        asyncore.dispatcher.close(self)

        # kill all threads
        for i in range(self.worker_threads*5):
            self.requestQueue.put(None)
        for i in self.threadPool:
            i.join()

        global SERVERS
        SERVERS -= 1
        
        # if it is the last one join the asyncore thread
        if SERVERS == 0:
            ASYNCORE_THREAD.join()
            asyncore.close_all()

class BaseRequestHandler(asyncore.dispatcher):
    "Base Request Handler Object"
    def __init__(self, server):
        self.server = server
        self.hasRequest = False
        self.hasResponse = False
        self.output_buffer = ''
        self.input_buffer = []
        self.sent = 0

    def activate(self, sock):
        self.set_socket(sock)

    def write_buffer(self, s):
        self.output_buffer += s

    def readable(self):
        return not self.hasRequest

    def writable(self):
        return self.hasResponse

    def handle_connect(self):
        pass

    def handle_close(self):
        pass

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.input_buffer.append(data)
        else:
            self.input_buffer = ''.join(self.input_buffer)
            self.hasRequest = True
            # put it in the queue so that is served
            self.server.requestQueue.put(self)

    def handle_write(self):
        if self.sent < len(self.output_buffer):
            self.sent += self.send(self.output_buffer[self.sent:self.sent + 8192])
            if self.sent > 262144:
                self.output_buffer = self.output_buffer[self.sent:]
                self.sent = 0
        else:
            self.shutdown(1)
            self.close()

    def close(self):
        asyncore.dispatcher.close(self)
        self.hasRequest = False
        self.hasResponse = False
        self.input_buffer = []
        self.output_buffer = ''
        self.sent = 0
        # put it in inactive request handlers queue
        self.server.rhQueue.put(self)
        self.server.activeConnections -= 1
        # print 'Total: ' + str(self.server.activeConnections)

    def handleRequest(self):
        pass


class BaseRequest(object):
    def __init__(self, buffer=''):
        self.buffer = buffer

    def getResponse(self, address):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        try:
            # TODO: remove this try
            # THIS TRY IS FOR DEBUGGING PURPOSES
            try:
                err = s.connect_ex(address)
                while not err in (0, EISCONN):
                    if err == EADDRINUSE:  # address already in use
                        # the ephemeral port range is exhausted
                        s.close()
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.bind((SERVER_IP, nextPort(address)))
                    else:
                        # the host refuses conncetion
                        break
                    err = s.connect_ex(address)

                s.send(self.buffer)
                s.shutdown(1)
                # Get the response object from master
                response = []
                
                rdata = s.recv(8192)
                while rdata:
                    response.append(rdata)
                    rdata = s.recv(8192)
            except socket.error, v:
                import traceback, sys
                output = traceback.format_exception(*sys.exc_info())
                output = ''.join(output)
                print output
                raise

        finally:
            s.close()

        sResponse = ''.join(response)
        return(sResponse)
