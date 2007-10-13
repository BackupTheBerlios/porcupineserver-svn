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
"Request classes"

from cgi import parse_qs, FieldStorage
import Cookie
import cStringIO

from porcupine.core import xmlrpc

class Request(object):
    """Base request class

    @ivar item: If the request addresses a Porcupine object, then this
    attribute contains this object, otherwise None.
    @type item: L{GenericItem<porcupine.systemObjects.GenericItem>}
    
    @ivar serverVariables: The request environment
    @type serverVariables: dict
    
    @ivar queryString: The query string parameters as lists.
    @type queryString: dict

    @ivar cookies: Contains the cookies sent by the client
    @type cookies: Cookie.SimpleCookie
    
    @ivar input: The raw request input
    @type input: StringIO

    @ivar interface: The request's interface, i.e. 'CGI' or 'MOD_PYTHON' or 'WSGI'
    @type interface: str
    """
    def __init__(self, rawRequest):
        self.serverVariables = rawRequest['env']
        self.serverVariables.setdefault('HTTP_ACCEPT_LANGUAGE', '')
        
        if self.serverVariables.setdefault('QUERY_STRING', ''):
            self.queryString = parse_qs(self.serverVariables['QUERY_STRING'])
        else:
            self.queryString = {}
        
        self.cookies = Cookie.SimpleCookie()
        if self.serverVariables.has_key('HTTP_COOKIE'):
            self.cookies.load(self.serverVariables['HTTP_COOKIE'])
        
        self.input = cStringIO.StringIO(rawRequest['inp'])
        self.interface = rawRequest['if']
        self.item = None

    def getLang(self):
        """Returns the preferred language of the client.
        If the client has multiple languages selected, the first is returned.
        
        @rtype: str
        """
        return(self.serverVariables['HTTP_ACCEPT_LANGUAGE'].split(',')[0])
        
    def getHost(self):
        """Returns the name of the host.
        
        @rtype: str
        """
        return(self.serverVariables["HTTP_HOST"])

    def getQueryString(self):
        """Returns the full query string, including the '?'.
        
        @rtype: str
        """
        if self.serverVariables['QUERY_STRING']:
            return '?' + self.serverVariables['QUERY_STRING']
        else:
            return ''
        
    def getProtocol(self):
        """Returns the request's protocol (http or https).
        
        @rtype: str
        """
        sProtocol = 'http'
        if self.serverVariables.setdefault('HTTPS', 'off') == 'on':
            sProtocol += 's'
        return(sProtocol)

    def getRootUrl(self):
        """Returns the site's root URL including the executing script.
        For instance, C{http://server/porcupine.py}
        
        @rtype: str
        """
        return (self.getProtocol() + '://'
                + self.serverVariables['HTTP_HOST']
                + self.serverVariables['SCRIPT_NAME'])

class HTTPRequest(Request):
    """This type of request is used by the
    L{porcupine.core.servlet.HTTPServlet} class.
   
    @ivar form: If the request method is POST, this attribute holds the posted
                values.
    @type form: dict
    """
    def __init__(self, req):
        self.serverVariables = req.serverVariables
        self.interface = req.interface
        self.item = req.item
        self.input = req.input
        self.cookies = req.cookies
        self.queryString = req.queryString
        self.form = FieldStorage(fp=req.input, environ=req.serverVariables)

class XMLRPCRequest(Request):
    """This type of request is used by the
    L{porcupine.core.servlet.XMLRPCServlet} class.
    You won't ever need to use this directly, since this kind of request is
    handled automatically by the servlet internally.
    """
    def __init__(self, req):
        self.serverVariables = req.serverVariables
        self.interface = req.interface
        self.item = req.item
        self.params = xmlrpc.XMLRPCParams()
        self.cookies = req.cookies
        self.params.loadXML(req.input.getvalue())
