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
Porcupine base classes for multi processing, multi threaded network servers
"""
import signal
import socket
import time
import Queue
from threading import Thread, currentThread
try:
    import multiprocessing
except ImportError:
    multiprocessing = None

from porcupine.core import asyncore
from porcupine.core.servicetypes.service import BaseService

class BaseServerThread(Thread):
    def handle_request(self, request_handler):
        raise NotImplementedError

class BaseServer(BaseService, asyncore.dispatcher):
    "Base class for threaded TCP server using asynchronous sockets"
    def __init__(self, name, address, worker_processes, worker_threads,
                 thread_class):
        # initialize base service
        BaseService.__init__(self, name)
        self.addr = address
        self.worker_processes = worker_processes
        self.worker_threads = worker_threads
        self.thread_class = thread_class
        self.is_multiprocess = multiprocessing and worker_processes > 0

        if self.is_multiprocess:
            self.request_queue = multiprocessing.Queue(worker_threads * 2)
            self.done_queue = multiprocessing.Queue(worker_threads *
                                                    worker_processes)
        else:
            self.request_queue = Queue.Queue(worker_threads * 2)

        # create queue for inactive RequestHandler objects i.e. those served
        self.rh_queue = Queue.Queue(0)
        # create worker tuple
        self.worker_pool = []

    def start(self):
        # activate socket
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.bind(self.addr)
        except socket.error, v:
            self.close()
            raise v

        self.listen(32)

        if self.is_multiprocess:
            self.task_dispatchers = []
            for i in range(self.worker_processes):
                pname = '%s server process %d' % (self.name, i+1)
                p = SubProcess(pname, self.worker_threads,
                               self.thread_class,
                               self.request_queue, self.done_queue)
                p.start()
                self.worker_pool.append(p)
            # start task dispatcher threads
            for i in range(self.worker_processes):
                t = Thread(target=self.task_dispatch,
                           name='%s task dispatcher %d' % (self.name, i+1))
                t.start()
                self.task_dispatchers.append(t)
        else:
            for i in range(self.worker_threads):
                tname = '%s server thread %d' % (self.name, i+1)
                t = self.thread_class(target=self.thread_loop, name=tname)
                t.start()
                self.worker_pool.append(t)

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
            rh = RequestHandler(self)
        # set the client socket of requestHandler
        self.active_connections += 1
        client_socket.setblocking(0)
        rh.activate(client_socket)

    def task_dispatch(self):
        while True:
            next = self.done_queue.get()
            if next == None:
                break
            fd, buffer = next
            try:
                if buffer == None:
                    asyncore.socket_map[fd].has_response = True
                else:
                    asyncore.socket_map[fd].write_buffer(buffer)
            except KeyError:
                pass

    def thread_loop(self):
        "loop for threads serving content to clients"
        thread = currentThread()
        while True:
            # get next waiting client request
            request_handler = self.request_queue.get()
            if request_handler == None:
                break
            else:
                if request_handler.input_buffer:
                    thread.handle_request(request_handler)
                    request_handler.has_response = True
                else:
                    # we have a dead socket(?)
                    request_handler.close()

    def shutdown(self):
        if self.running:
            self.running = False
            self.close()
            asyncore.dispatcher.close(self)
            # kill all threads/processes
            if self.is_multiprocess:
                for i in range(len(self.task_dispatchers)):
                    self.done_queue.put(None)
                for t in self.task_dispatchers:
                    t.join()
            for i in range(self.worker_threads * 2):
                self.request_queue.put(None)
            for t in self.worker_pool:
                t.join()

class RequestHandler(asyncore.dispatcher):
    "Request handler object"
    def __init__(self, server):
        self.server = server
        self.has_request = False
        self.has_response = False
        self.output_buffer = ''
        self.input_buffer = []

    def activate(self, sock):
        self.set_socket(sock)

    def write_buffer(self, s):
        self.output_buffer += s

    def readable(self):
        return not self.has_request

    def writable(self):
        return self.has_request

    def handle_connect(self):
        pass

    def handle_close(self):
        pass

    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.input_buffer.append(data)
        else:
            self.has_request = True
            self.input_buffer = ''.join(self.input_buffer)
            if self.server.is_multiprocess:
                proxy = RequestHandlerProxy(self)
                self.server.request_queue.put(proxy)
            else:
                # put it in the queue so that is served
                self.server.request_queue.put(self)

    def handle_write(self):
        if len(self.output_buffer):
            sent = self.send(self.output_buffer)
            self.output_buffer = self.output_buffer[sent:]
        elif self.has_response:
            self.close()

    def close(self):
        asyncore.dispatcher.close(self)
        self.has_request = False
        self.has_response = False
        self.input_buffer = []
        self.output_buffer = ''
        # put it in inactive request handlers queue
        self.server.rh_queue.put(self)
        self.server.active_connections -= 1
        # print 'Total: ' + str(self.server.active_connections)

if multiprocessing:
    class RequestHandlerProxy(object):
        def __init__(self, rh):
            self.fd = rh._fileno
            self.input_buffer = rh.input_buffer
            self.done_queue = None

        def write_buffer(self, s):
            self.done_queue.put((self.fd, s))

        def close(self):
            pass

    class SubProcess(BaseService, multiprocessing.Process):
        def __init__(self, name, worker_threads, thread_class,
                     request_queue, done_queue):
            multiprocessing.Process.__init__(self, name=name)
            self.worker_threads = worker_threads
            self.thread_class = thread_class
            self.request_queue = request_queue
            self.done_queue = done_queue
            self.thread_pool = []

        def shutdown(self, arg1=None, arg2=None):
            from porcupine.core import runtime
            runtime.shutdown()

        def start(self):
            multiprocessing.Process.start(self)

        def run(self):
            # load configuration settings
            self.init_config()
            # init db without the maintanance thread which runs in the root
            # process
            self.init_db(init_maintenance=False)
            # inititialize session manager without the expiration mechanism
            # which runs in the root process
            self.init_session_manager(init_expiration=False)

            for i in range(self.worker_threads):
                tname = '%s thread %d' % (self.name, i+1)
                t = self.thread_class(target=self._thread_loop, name=tname)
                self.thread_pool.append(t)

            # start threads
            [t.start() for t in self.thread_pool]

            signal.signal(signal.SIGINT, self.shutdown)
            signal.signal(signal.SIGTERM, self.shutdown)
            try:
                while self.is_alive():
                    time.sleep(30.0)
            except IOError:
                pass

        def _thread_loop(self):
            "subprocess loop for threads serving content to clients"
            thread = currentThread()
            while True:
                # get next waiting client request
                request_handler = self.request_queue.get()
                if request_handler == None:
                    break
                else:
                    request_handler.done_queue = self.done_queue
                    if request_handler.input_buffer:
                        thread.handle_request(request_handler)
                        self.done_queue.put((request_handler.fd, None))

