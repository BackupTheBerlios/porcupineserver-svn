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
"Porcupine base threaded TCP-IP server"

from socket import *
import Queue, select
from time import clock
from marshal import dumps, loads
##import hotshot

int_length = len(dumps(int(1)))

class BaseServer(object):
    "Implements threaded tcp server"
    def __init__(self, name, address, port, worker_threads, threadClass, requestHandler):
        # create server socket
        self.name = name
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.addr = (address, port)
        self.serverSocket.bind(self.addr)
        self.running = True

        if False:
            self.prof = hotshot.Profile("C:/Web Projects/Porcupine/Server/profiler/hotshot.prof")

        # create client request queue
        self.worker_threads = worker_threads
        self.requestQueue = Queue.Queue(worker_threads*2)
        # create queue for inactive requestHandler objects i.e. those served
        self.rhQueue = Queue.Queue(0)
        # create threads tuple
        self.threadPool = []

        for i in range(worker_threads):
            t = threadClass(target=self.threadLoop)
            t.start()
            self.threadPool.append(t)
        # activate socket
        self.serverSocket.listen(64)
        self.requestHandler = requestHandler

    def start(self):
        "Main loop of Base Server. Waits for client connections"
        from errno import EINTR

        while self.running:
            try:
                #wait for input in listening socket
                input, output, exc = select.select([self.serverSocket], [], [], 1)
            except select.error, v:
                if v[0]==EINTR or v[0]==0:
                    break
                else:
                    raise
            if self.running:
                for sock in input:
                    ##rh = None
                    # accept client connection
                    clientSocket, addr = sock.accept()
                    try:
                        # get inactive requestHandler from queue
                        rh = self.rhQueue.get_nowait()
                    except Queue.Empty:
                        # if empty then create new requestHandler
                        rh = self.requestHandler(self)
                    # set the client socket of requestHandler and finally
                    # put it in queue for threads to serve this request
                    rh.setClient(clientSocket)
                    self.requestQueue.put(rh)

    def threadLoop(self):
        "loop for threads serving content to clients"
        while True:
            try:
                # get next waiting client request
                rh = self.requestQueue.get()
                if rh == None:
                    break
                else:
                    if self.running:
                        ## get start time
                        ## t = clock()
                        if True:
                            rh.handleRequest()
                        else:
                            self.prof.runcall(rh.handleRequest)
                        ##t = clock() - t
                        ##print 'Benchmark: %s' % str(t)
                    # deactivate requesthandler object and put it in rhQueue
                    rh.close()
            except Queue.Empty:
                pass

    def awakeSelect(self):
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.connect(self.addr)
            sock.close()
        except:
            pass
        return

    def shutdown(self):
        self.running = False
        self.awakeSelect()
        self.serverSocket.close()
        
        # kill all threads
        for i in range(self.worker_threads*2):
            self.requestQueue.put(None)
        for i in self.threadPool:
            i.join()
        if False:
            self.prof.close()

class BaseRequestHandler(object):
    "Base Request Handler Object"
    def __init__(self, server):
        self.server = server
        self.chunk = ''

    def setClient(self, clientSocket):
        self.sock = clientSocket

    def close(self):
        self.sock.close()
        self.sock = None
        self.chunk = ''
        self.server.rhQueue.put(self)

    def handleRequest(self):
        # get request length
        chunk = ''
        while len(chunk) < int_length:
            chunk = chunk + self.sock.recv(int_length)
        requestLength = loads(chunk)
        # get request
        chunk = ''
        missing = requestLength
        while missing > 0:
            chunk = chunk + self.sock.recv(missing)
            missing = requestLength - len(chunk)
        #no more receives
        self.sock.shutdown(0)
        self.chunk = chunk
