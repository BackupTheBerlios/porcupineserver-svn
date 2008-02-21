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
"Porcupine Server Thread"

import re

from porcupine.config.settings import settings
from porcupine.config import pubdirs

from porcupine.core.http.context import HttpContext
from porcupine.core.http.request import HttpRequest
from porcupine.core.http.response import HttpResponse
from porcupine.core.http import ServerPage

from porcupine.db import dbEnv
from porcupine import exceptions
from porcupine.core.services.asyncBaseServer import BaseServerThread

class PorcupineThread(BaseServerThread):
    _method_cache = {}
    def __init__(self, target, name):
        BaseServerThread.__init__(self, target, name)
        self.context = None
        self.trans = None

    def get_response(self, raw_request):
        response = HttpResponse()
        request = HttpRequest(raw_request)
                
        item = None
        registration = None
        
        try:
            try:
                self.context = HttpContext(request, response)
                sPath = request.serverVariables['PATH_INFO']
                try:
                    item = dbEnv.getItem(sPath)
                except exceptions.ObjectNotFound:
                    # dir request
                    lstPath = sPath.split('/')
                    dirName = lstPath[1]
                    # remove blank entry & app name to get the requested path
                    sDirPath = '/'.join(lstPath[2:])
                    webApp = pubdirs.dirs.setdefault(dirName, None)
                    if webApp:
                        registration = webApp.getRegistration(
                            sDirPath,
                            request.serverVariables['REQUEST_METHOD'],
                            request.serverVariables['HTTP_USER_AGENT'],
                            request.getLang())
                    if not registration:
                        raise exceptions.NotFound, \
                            'The resource "%s" does not exist' % sPath
                    
                    # apply pre-processing filters
                    [filter[0].apply(self.context, registration, **filter[1])
                     for filter in registration.filters
                     if filter[0].type == 'pre']
                
                    rtype = registration.type
                    if rtype == 1: # psp page
                        ServerPage.execute(self.context, registration.context)
                    elif rtype == 0: # static file
                        response.loadFromFile(registration.context)
                        if registration.encoding:
                            response.charset = registration.encoding
                else:
                    # db request
                    if (item == None):
                        raise exceptions.PermissionDenied
                    self.dispatch_method(item)
            
            except exceptions.ResponseEnd, e:
                pass
            
            if registration != None:
                # do we have caching directive?
                if registration.max_age:
                    response.setExpiration(registration.max_age)
                # apply post-processing filters
                [filter[0].apply(self.context, registration, **filter[1])
                 for filter in registration.filters
                 if filter[0].type == 'post']

        except exceptions.InternalRedirect, e:
            lstPathInfo = e.args[0].split('?')
            raw_request['env']['PATH_INFO'] = lstPathInfo[0]
            if len(lstPathInfo == 2):
                raw_request['env']['QUERY_STRING'] = lstPathInfo[1]
            else:
                raw_request['env']['QUERY_STRING'] = ''
            self.get_response(raw_request)
            
        except exceptions.PorcupineException, e:
            e.emit(self.context, item)
                
        except exceptions.ProxyRequest, e:
            raise e
        
        except:
            e = exceptions.InternalServerError()
            e.emit(self.context, item)
        
        # abort uncommited transaction
        if self.trans != None and not self.trans._iscommited:
            self.trans.abort()
        self.trans = None
        
        settings['requestinterfaces'][request.interface](
              self.requestHandler, response)

    def dispatch_method(self, item):
        method_name = self.context.request.method or '__blank__'
        method = None
        
        # get request parameters
        r_http_method = self.context.request.serverVariables['REQUEST_METHOD']
        r_browser = self.context.request.serverVariables['HTTP_USER_AGENT']
        r_qs = self.context.request.serverVariables['QUERY_STRING']
        r_lang = self.context.request.getLang()
        
        method_key = (item.__class__, method_name, r_http_method,
                      r_qs, r_browser, r_lang)
        
        method = self._method_cache.get(method_key, None)
        if method == None:
            candidate_methods = [meth for meth in dir(item)
                                 if meth[:4+len(method_name)] == \
                                 'WM_%s_' % method_name]
            
            candidate_methods.sort(
                cmp=lambda x,y:-cmp(len(getattr(item,x).func_dict['cnd'][3]),
                                    len(getattr(item,y).func_dict['cnd'][3])))
            
            for method_name in candidate_methods:
                http_method, client, lang, qs = \
                    getattr(item, method_name).func_dict['cnd']
            
                if re.match(http_method, r_http_method) and \
                        re.search(qs, r_qs) and \
                        re.search(client, r_browser) and \
                        re.match(lang, r_lang):
                    method = method_name
                    break
        
            self._method_cache[method_key] = method
    
        if method == None:
            raise exceptions.NotFound, \
                'Invalid method call "%s"' % method_name
        else:
            # execute method
            getattr(item, method)(self.context)
