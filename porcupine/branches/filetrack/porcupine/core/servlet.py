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
"Base Servlet classes"

import sys, os.path
from threading import currentThread

from porcupine.db import db
from porcupine.security import objectAccess
from porcupine import serverExceptions
import porcupine.core.request
import porcupine.core.response
import porcupine.core.xmlrpc

class BaseServlet(object):
    """Base Servlet class
    
    @ivar server: Gives access to the server database
    @type server: L{Server<porcupine.core.serverProxy.Server>}
    
    @ivar session: The current session object
    @type session: L{Session<porcupine.security.session.Session>}
    
    @ivar request: The current request object
    @type request: L{Request<porcupine.core.request.Request>}
    
    @ivar item: If the request addresses a Porcupine object, then this
    attribute contains this object, otherwise None.
    @type item: L{GenericItem<porcupine.systemObjects.GenericItem>}
    """
    def __init__(self, server, session, request):
        self.server = server
        self.session = session
        self.request = request
        self.item = request.item
        
        if self.item:
            if objectAccess.getAccess(self.item, self.session.user) == objectAccess.NO_ACCESS:
                raise serverExceptions.PermissionDenied

    def runAsSystem(self):
        """Causes the servlet to run under the SYSTEM account.
        Use this method carefully, since it gives full access rights to
        the Porupine database.
        
        @return: None
        """
        currentThread().session.user = db.getItem('system')

    def execute(self):
        """The servlet implementation method. Override this, to implement your
        servlets.
        
        @return: None
        """
        raise NotImplementedError

class HTTPServlet(BaseServlet):
    """
    HTTP servlet class
    
    @ivar request: The current HTTP request object
    @type request: L{HTTPRequest<porcupine.core.request.HTTPRequest>}
    
    @ivar response: The HTTP response
    @type response: L{HTTPResponse<porcupine.core.response.HTTPResponse>}
    
    """
    def __init__(self, server, session, request):
        BaseServlet.__init__(self, server, session, request)
        self.request = request = porcupine.core.request.HTTPRequest(self.request)
        self.response = currentThread().response = porcupine.core.response.HTTPResponse()

    def include(self, func):
        """Executes the given function inside the servlet's context.
        
        @param func: The function to be executed.
        @type func: function
        
        @return: None
        """
        exec func.func_code in self.__dict__

class XMLRPCServlet(BaseServlet):
    """
    XML-RPC Servlet
    ===============
    The methods of this type of servlet become HTTP accessible, via XML-RPC.
    
    @ivar request: The current XML-RPC request
    @type request: L{XMLRPCRequest<porcupine.core.request.XMLRPCRequest>}
    
    @ivar response: The XML-RPC response
    @type response: L{XMLRPCResponse<porcupine.core.response.XMLRPCResponse>}
    """
    def __init__(self, server, session, request):
        BaseServlet.__init__(self, server, session, request)
        self.request = request = porcupine.core.request.XMLRPCRequest(self.request)
        self.response = currentThread().response = porcupine.core.response.XMLRPCResponse()

    def execute(self):
        """This method deserializes the request, calls the requested method
        with the given parameters and finally serializes the method's return
        value.
        
        @warning: do not override
        """
        try:
            method = getattr(self, self.request.params.method)
        except AttributeError:
            raise serverExceptions.XMLRPCError, 'Invalid remote method "%s"' % self.request.params.method
        args = tuple(self.request.params)
        output = method(*args)
        if output is not None:
            self.response.params = porcupine.core.xmlrpc.XMLRPCParams((output,))
        else:
            raise serverExceptions.XMLRPCError, 'Remote method "%s" returns no parameters' % self.request.params.method

class XULServlet(HTTPServlet):
    """
    QuiX XUL Servlet
    ================
    This type is used for writting QuiX XUL content.
    
    @ivar isPage: Indicates if the response is an HTML page.
        If set to C{True} the servlet adds the required boilerplate
        required to initialize the QuiX engine. This is normally required for
        the first request.
    @type isPage: bool
    
    @ivar params: Parameter values. The QuiX XUL interface is written to the
        response using the '%' formatting operator.
    @type params: dict

    @ivar xul_file: The path to the QuiX XUL file. This is automatically set to
        C{[module_name].[class_name].xul}, but this can be overriden.
    @type xul_file: str
    """
    def __init__(self, server, session, request):
        HTTPServlet.__init__(self, server, session, request)
        self.params = {}
        self.isPage = False
        #sPath = os.path.sep.join(self.__class__.__module__.split('.'))
        #self.xul_file = '%s.%s.xul' % (sPath, self.__class__.__name__)
        class_dir = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        self.xul_file = '%s%s%s.%s.xul' % (class_dir, os.path.sep, self.__module__.split('.')[-1], self.__class__.__name__)
        
    def execute(self):
        """This method opens the QuiX XUL definition and writes it to
        the response buffer using the parameters provided.
        
        @warning: do not override
        """
        self.setParams()
        # open XUL file
        try:
            oFile = file(self.xul_file)
        except IOError:
            raise serverExceptions.InvalidRegistration, 'XUL file "%s" is missing' % self.xul_file

        if self.isPage:
            self.response.write('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html>
    <head>
        <script type="text/javascript" defer="defer" src="%s/__xul/quixextensions.js"></script>
        <script type="text/javascript" defer="defer" src="%s/__xul/xul_core.js"></script>
        <script type="text/javascript" defer="defer" src="%s/__xul/xmlrpc.js"></script>
        <link type="text/css" rel="stylesheet" href="%s/styles/quix.css"></link>
    </head>
    <body onload="__init__()">
        <xml id="xul" style="display:none">
''' % ((self.request.serverVariables["SCRIPT_NAME"],) * 4) )
        else:
            self.response.content_type = 'text/xml'
            
        try:
            self.response.write(oFile.read() % self.params)
        finally:
            oFile.close()

        if self.isPage:
            self.response.write('''
        </xml>
    </body>
</html>
''')
        
    def setParams(self):
        """This is where you should set the parameters found
        inside the QuiX interface definition file. Use the
        C{self.params} dictionary.
        """
        pass