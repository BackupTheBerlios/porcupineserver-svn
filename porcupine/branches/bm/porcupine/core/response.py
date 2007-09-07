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
"Response classes"

import re, os, Cookie
import time
from threading import currentThread

from porcupine.utils import xmlUtils
from porcupine import serverExceptions
from porcupine.config.settings import settings

HTTP_ERROR_PAGE = 'conf/errorpage.html'
XMLRPC_ERROR_PAGE = 'conf/XMLRPCError.xml'

class BaseResponse(object):
    """Base response class

    @ivar content_type: Sets the content type of the response
    @type content_type: str
    
    @ivar charset: Sets the response's character encoding
    @type charset: str

    @ivar cookies: Using this variable you can set cookies
                   to be accepted by the client (if they are allowed)
    @type cookies: Cookie.SimpleCookie
    """
    def __init__(self):
        self.__headers = {}
        self.cookies = Cookie.SimpleCookie()
        self.content_type = 'text/html'
        self.charset = 'utf-8'
        self._body = []
    
    def setExpiration(self, iSeconds):
        """The response becomes valid for a certain amount of time
        expressed in seconds. The response is cached and reused for x seconds
        without server roundtripping.
        
        @param iSeconds: number of seconds
        @type iSeconds: int
            
        @return: None
        """
        self.__headers['Cache-Control'] = 'max-age=' + str(iSeconds) + ',public'
        self.__headers['Expires'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time() + iSeconds))

    def _reset(self):
        self.__init__()
        
    def clear(self):
        "Clears the response body."
        self._body = []
        
    def setHeader(self, header, value):
        """Sets a response HTTP header.

        @param header: HTTP header name e.g. 'Content-Type'
        @type header: str
        @param value: HTTP header value e.g. 'text/xml'
        @type value: str
        
        @return: None
        """
        self.__headers[header] = value
        
    def _getHeaders(self):
        ct = self.content_type
        if ct:
            if self.charset and ct[0:4]=='text':
                ct += '; charset=' +  self.charset
            self.__headers['Content-Type'] = ct
        return self.__headers

    def redirect(self, location):
        """Causes the client to redirect to a specified location.
        Relative redirects are not safe.

        @param location: redirect location
        @type location: str
        
        @return: None
        """
        #self.__headers.clear()
        self.__headers["Location"] = location
        raise serverExceptions.ResponseEnd

    def internal_redirect(self, location):
        """Internal server transfer
        
        @param location: internal relative location
        @type location: str
        
        @return: None
        """
        raise serverExceptions.InternalServerRedirect, \
                location

    def _getBody(self):
        return(''.join(self._body))

    def loadFromFile(self, fileName):
        """Loads the response body from a file that resides on the file
        system and sets the 'Content-Type' header accordingly.
        
        @param fileName: path of the file to be loaded
        @type fileName: str
        
        @return: None
        """
        try:
            oFile = file(fileName, 'rb')
        except IOError:
            raise serverExceptions.InvalidRegistration, \
                    'The file "%s" could not be found' % fileName
        
        sFileExt = fileName.split('.')[-1]
        self.content_type = settings['mediatypes'].setdefault(sFileExt,
                                                              'text/plain')
        sResponseBody = oFile.read()
        self._body = [sResponseBody]

    def _writeError(self, exc):
        self._reset()
        iCode = exc.code
        sDescr = exc.description
        request = currentThread().request
        
        sMethod = request.serverVariables['REQUEST_METHOD']
        sBrowser = request.serverVariables['HTTP_USER_AGENT']
        sLang = request.serverVariables['HTTP_ACCEPT_LANGUAGE']
        
        if request.item:
            sItemCC = request.item.contentclass
        else:
            sItemCC = '-'

        if request.queryString.has_key('cmd'):
            sCmd = request.queryString['cmd'][0]
        else:
            sCmd = '-'

        if exc.outputTraceback:
            import sys, traceback
            sInfo = traceback.format_exception(*sys.exc_info())
            sInfo = '<br>'.join(sInfo)
        else:
            sInfo = exc.info

        self.__headers['Cache-Control'] = 'no-cache'
        oFile = open(HTTP_ERROR_PAGE)
        sBody = oFile.read()
        oFile.close()
        self._body.append(sBody % vars())
    
class HTTPResponse(BaseResponse):
    """The response type used by the
    L{porcupine.core.servlet.HTTPServlet} class.
    """
    def write(self, s):
        """Appends a string to the response sent to the client.
        
        @param s: string to write
        @type s: str
        
        @return: None
        """
        self._body.append(str(s))

    def end(self):
        """Terminates the response processing cycle
        and sends the response written so far to the client."""
        raise serverExceptions.ResponseEnd

    def writeFile(self, sFilename, sStream, isAttachment=True):
        """Writes a file stream to the response using a specified
        filename.

        @param sFilename: file name
        @type sFilename: str
        @param sStream: file stream
        @type sStream: str
        @param isAttachment: If C{True} then the file is sent as an attachment.
        @type isAttachment: bool

        @return: None
        """
        if isAttachment:
            sPrefix = 'attachment;'
        else:
            sPrefix = ''
        sFileExt = sFilename.split('.')[-1]
        self.content_type = settings.mediatypes.setdefault(sFileExt, 'text/plain')
        self.setHeader('Content-Disposition', sPrefix + 'filename=' + sFilename)
        self._body = [sStream]
        
class XMLRPCResponse(BaseResponse):
    """The response type used by the L{porcupine.core.servlet.XMLRPCServlet}
    class. You won't ever need to instantiate this, since this kind of
    response is handled by the servlet internally.
    """
    def __init__(self):
        BaseResponse.__init__(self)
        self.params = None
        self.content_type = 'text/xml'
        self.__hasFault = False

    def _getBody(self):
        if self.__hasFault:
            return(''.join(self._body))
        else:
            return('<?xml version="1.0"?><methodResponse>%s</methodResponse>' %
                    self.params.serialize())

    def _writeError(self, exc):
        self._reset()
        self.__hasFault = True
        iCode = exc.code
        sDescr = exc.description
        
        if exc.info:
            sDescr += '\n' + exc.info

        if exc.outputTraceback:
            import sys, traceback
            sDescr += '\n'
            sInfo = traceback.format_exception(*sys.exc_info())
            sDescr += '\n'.join(sInfo)

        self.setHeader('Cache-Control', 'no-cache')

        oFile = open(XMLRPC_ERROR_PAGE)
        sBody = oFile.read()
        oFile.close()
        self._body.append( sBody % (iCode, xmlUtils.XMLEncode(sDescr)) )

