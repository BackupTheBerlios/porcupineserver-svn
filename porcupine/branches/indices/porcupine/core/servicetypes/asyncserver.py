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
import sys
import socket
import time
import Queue
import select
from threading import Thread, currentThread
try:
    import multiprocessing
    if sys.platform == 'win32':
        import multiprocessing.reduction
except ImportError:
    multiprocessing = None

from porcupine.core import asyncore
from porcupine.core.servicetypes.service import BaseService

class BaseServerThread(Thread):
    def handle_request(self, request_handler):
        raise NotImplementedError

class Dispatcher(asyncore.dispatcher):
    def __init__(self, request_queue, done_queue=None, socket_map=None):
        # create queue for inactive RequestHandler objects i.e. those served
        self.rh_queue = Queue.Queue(0)
        self.active_connections = 0
        self.request_queue = request_queue
        self.done_queue = done_queue
        self.socket_map = socket_map

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
        rh.activate(client_socket, self.socket_map)

class BaseServer(BaseService, Dispatcher):
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
        self.task_dispatchers = []

        request_queue = None
        done_queue = None

        if self.is_multiprocess:
            if not hasattr(socket, 'fromfd'):
                # create multiprocessing queues for communicating
                request_queue = multiprocessing.Queue(worker_threads *
                                                      worker_processes)
                done_queue = multiprocessing.Queue(worker_threads *
                                                   worker_processes)
        else:
            request_queue = Queue.Queue(worker_threads * 2)

        Dispatcher.__init__(self, request_queue, done_queue)

        # create worker tuple
        self.worker_pool = []

    def start(self):
        # start runtime services
        BaseService.start(self)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(0)
        try:
            sock.bind(self.addr)
        except socket.error, v:
            sock.close()
            raise v
        sock.listen(64)

        if self.request_queue != None:
            self.accepting = 1
            # activate server socket
            self.set_socket(sock)

        if self.is_multiprocess:
            if self.request_queue == None:
                # start worker processes
                for i in range(self.worker_processes):
                    pname = '%s server process %d' % (self.name, i+1)
                    p = SubProcess(pname,
                                   self.worker_threads,
                                   self.thread_class,
                                   None,
                                   None,
                                   sock)
                    p.start()
                    self.worker_pool.append(p)
            else:
                # start worker processes
                for i in range(self.worker_processes):
                    pname = '%s server process %d' % (self.name, i+1)
                    p = SubProcess(pname,
                                   self.worker_threads,
                                   self.thread_class,
                                   self.request_queue,
                                   self.done_queue)
                    p.start()
                    self.worker_pool.append(p)
                
                # start task dispatcher thread(s)
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

        self.running = True

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
        "loop for threads serving content to clients (non mutltiprocessing)"
        thread = currentThread()
        while True:
            # get next waiting client request
            request_handler = self.request_queue.get()
            if request_handler == None:
                break
            else:
                thread.handle_request(request_handler)
                request_handler.has_response = True

    def shutdown(self):
        if self.running:
            self.running = False
            if self.request_queue:
                if self.is_multiprocess:
                    qlen = self.worker_processes * self.worker_threads
                else:
                    qlen = self.worker_threads * 2
                Dispatcher.close(self)
                for i in range(qlen):
                    self.request_queue.put(None)

            # join workers
            for t in self.worker_pool:
                t.join()

            if self.done_queue:
                # we have multiprocessing queues
                # join task dispatchers
                for i in range(self.worker_processes):
                    self.done_queue.put(None)
                for t in self.task_dispatchers:
                    t.join()
                self.request_queue.close()
                self.done_queue.close()
                self.request_queue.join_thread()
                self.done_queue.join_thread()

            # shut down runtime services
            BaseService.shutdown(self)

class RequestHandler(asyncore.dispatcher):
    "Request handler object"
    def __init__(self, server):
        self.server = server
        self.has_request = False
        self.has_response = False
        self.output_buffer = ''
        self.input_buffer = []

    def activate(self, sock, socket_map=None):
        self.set_socket(sock, socket_map)

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
            self.input_buffer = ''.join(self.input_buffer)
            if self.input_buffer:
                self.has_request = True
                if self.server.done_queue != None:
                    proxy = RequestHandlerProxy(self)
                    self.server.request_queue.put(proxy)
                else:
                    # put it in the queue so that is served
                    self.server.request_queue.put(self)
            else:
                # we have a dead socket(?)
                self.close()

    def handle_write(self):
        if len(self.output_buffer):
            sent = self.send(self.output_buffer)
            self.output_buffer = self.output_buffer[sent:]
        elif self.has_response:
            self.close()

    def close(self):
        asyncore.dispatcher.close(self)
        if self.server.socket_map != None:
            self.del_channel(self.server.socket_map)
        self.has_request = False
        self.has_response = False
        self.input_buffer = []
        self.output_buffer = ''
        if self.server != None:
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
        runtime_services = [('config', (), {}),
                            ('db', (), {'init_maintenance':False}),
                            ('session_manager', (), {'init_expiration':False})]

        def __init__(self, name, worker_threads, thread_class,
                     request_queue = None, done_queue = None, socket = None):
            BaseService.__init__(self, name)
            multiprocessing.Process.__init__(self, name=name)
            self.worker_threads = worker_threads
            self.thread_class = thread_class
            self.request_queue = request_queue
            self.done_queue = done_queue
            self.socket = socket

        def start(self):
            multiprocessing.Process.start(self)

        def _async_loop(self, socket_map):
            _use_poll = False
            if hasattr(select, 'poll'):
                _use_poll = True
            try:
                asyncore.loop(16.0, _use_poll, socket_map)
            except select.error, v:
                if v[0] == EINTR:
                    print 'Shutdown not completely clean...'
                else:
                    pass

        def run(self):
            # start runtime services
            BaseService.start(self)

            # start server
            if self.socket != None:
                socket_map = {}
                
                # start server
                self.request_queue = Queue.Queue(self.worker_threads * 2)
                self.done_queue = None
                server = Dispatcher(self.request_queue, None, socket_map)
                server.accepting = 1
                # activate server socket
                server.set_socket(self.socket, socket_map)

                # start asyncore loop
                asyn_thread = Thread(target=self._async_loop,
                                     args=(socket_map, ),
                                     name='%s asyncore thread' % self.name)
                asyn_thread.start()

            thread_pool = []
            for i in range(self.worker_threads):
                tname = '%s thread %d' % (self.name, i+1)
                t = self.thread_class(target=self._thread_loop, name=tname)
                thread_pool.append(t)

            # start threads
            [t.start() for t in thread_pool]

            try:
                while self.is_alive():
                    time.sleep(30.0)
            except KeyboardInterrupt:
                pass
            except IOError:
                pass

            # join threads
            for t in thread_pool:
                t.join()

            if self.socket != None:
                # join asyncore thread
                asyncore.close_all(socket_map)
                asyn_thread.join()

            if self.done_queue:
                # we have multiprocessing queues
                self.request_queue.close()
                self.done_queue.close()
                self.request_queue.join_thread()
                self.done_queue.join_thread()

            # shutdown runtime services
            BaseService.shutdown(self)

        def _thread_loop(self):
            "subprocess loop for threads serving content to clients"
            thread = currentThread()
            while True:
                # get next waiting client request
                request_handler = self.request_queue.get()
                if request_handler == None:
                    break
                else:
                    if self.done_queue == None:
                        # we have a RequestHandler
                        thread.handle_request(request_handler)
                        request_handler.has_response = True
                    else:
                        # we have a RequestHandlerProxy
                        request_handler.done_queue = self.done_queue
                        thread.handle_request(request_handler)
                        self.done_queue.put((request_handler.fd, None))
