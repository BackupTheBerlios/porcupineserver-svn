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
Porcupine base classes for threaded network servers
"""
import socket
import Queue
from threading import Thread, currentThread

from porcupine.core import asyncore
from porcupine.core.servicetypes.service import BaseService

class BaseServerThread(Thread):
    def __init__(self, target, name):
        Thread.__init__(self, None, target, name)
        self.request_handler = None

class BaseServer(BaseService, asyncore.dispatcher):
    "Base class for threaded TCP server using asynchronous sockets"
    def __init__(self, name, address, worker_threads, thread_class,
                 request_handler):
        # initialize base service
        BaseService.__init__(self, name)
        self.addr = address
        self.worker_threads = worker_threads
        self.request_handler = request_handler
        self.thread_class = thread_class
        # create client request queue
        self.request_queue = Queue.Queue(worker_threads*5)
        # create queue for inactive requestHandler objects i.e. those served
        self.rh_queue = Queue.Queue(0)
        # create threads tuple
        self.thread_pool = []

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
            t = self.thread_class(target=self.thread_loop, name=tname)
            t.start()
            self.thread_pool.append(t)

        self.active_connections = 0
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
        client_socket, addr = self.accept()
        try:
            # get inactive requestHandler from queue
            rh = self.rh_queue.get_nowait()
        except Queue.Empty:
            # if empty then create new requestHandler
            rh = self.request_handler(self)
        # set the client socket of requestHandler
        self.active_connections += 1
        client_socket.setblocking(0)
        rh.activate(client_socket)

    def thread_loop(self):
        "loop for threads serving content to clients"
        thread = currentThread()
        while True:
            try:
                # get next waiting client request
                thread.request_handler = self.request_queue.get()
                if thread.request_handler == None:
                    break
                else:
                    if thread.request_handler.input_buffer:
                        thread.request_handler.handle_request()
                        thread.request_handler.hasResponse = True
                    else:
                        # we have a dead socket
                        thread.request_handler.close()
            except Queue.Empty:
                pass

    def shutdown(self):
        self.running = False

        self.close()
        asyncore.dispatcher.close(self)

        # kill all threads
        for i in range(self.worker_threads*5):
            self.request_queue.put(None)
        for i in self.thread_pool:
            i.join()

class BaseRequestHandler(asyncore.dispatcher):
    "Base Request Handler Object"
    def __init__(self, server):
        self.server = server
        self.hasRequest = False
        self.hasResponse = False
        self.output_buffer = ''
        self.input_buffer = []

    def activate(self, sock):
        self.set_socket(sock)

    def write_buffer(self, s):
        self.output_buffer += s

    def readable(self):
        return not self.hasRequest

    def writable(self):
        return self.hasRequest

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
            self.server.request_queue.put(self)

    def handle_write(self):
        if len(self.output_buffer):
            sent = self.send(self.output_buffer)
            self.output_buffer = self.output_buffer[sent:]
        elif self.hasResponse:
            #self.shutdown(1)
            self.close()

    def close(self):
        asyncore.dispatcher.close(self)
        self.hasRequest = False
        self.hasResponse = False
        self.input_buffer = []
        self.output_buffer = ''
        # put it in inactive request handlers queue
        self.server.rh_queue.put(self)
        self.server.active_connections -= 1
        # print 'Total: ' + str(self.server.active_connections)

    def handle_request(self):
        pass
