#===============================================================================
#    Copyright 2005, 2006 Tassos Koutsovassilis
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
"Server registrations"

import re
from xml.dom import minidom
from xml.parsers import expat

from porcupine import serverExceptions
from porcupine.utils import misc

def getFiltersList(contextNode):
    filterList = contextNode.getElementsByTagName('filter')
    filters = []
    for filterNode in filterList:
        type = filterNode.getAttribute('type').encode('iso-8859-1')
        filter = [misc.getCallableByName(type), {}]
        for attr in filterNode.attributes.keys():
            filter[1][str(attr)] = filterNode.getAttribute(attr).encode('iso-8859-1')
        filters.append( tuple(filter) )
    return tuple(filters)

class Registration(object):
    __slots__ = ('context', 'type', 'encoding', 'filters', 'max_age')
    def __init__(self, identifier, enc, filters, max_age):
        try:
            self.context = misc.getCallableByName(identifier)
            self.type = 2
        except:
            self.context = identifier
            if identifier[-4:] == '.psp':
                self.type = 1
            else:
                self.type = 0
        
        self.encoding = enc
        self.filters = filters
        self.max_age = int(max_age);

class App(object):
    def __init__(self, appNode):
        appName = appNode.getAttribute('name')
        self.path = appNode.getAttribute('path')
        self.__config = []
        self.__cache = {}
        configXML = minidom.parse(self.path + '/config.xml')
        contextList = configXML.getElementsByTagName('context')
        # construct action list
        for contextNode in contextList:
            sPath = contextNode.getAttribute('path')
            sMethod = contextNode.getAttribute('method')
            sBrowser = contextNode.getAttribute('client')
            sLang = contextNode.getAttribute('lang')
            sAction = contextNode.getAttribute('action')
            encoding = contextNode.getAttribute('encoding').encode('iso-8859-1') or None
            max_age = contextNode.getAttribute('max-age') or 0
            
            self.__config.append((
                (sPath, sMethod, sBrowser, sLang),
                Registration(self.path + '/' + sAction, encoding,
                             getFiltersList(contextNode), max_age)
            ))
            
        configXML.unlink()

    def getRegistration(self, sPath, sHttpMethod, sBrowser, sLang):
        if self.__cache.has_key((sPath, sHttpMethod, sBrowser, sLang)):
            return self.__cache[(sPath, sHttpMethod, sBrowser, sLang)]
        else:
            for paramList in self.__config:
                Path, HttpMethod, Browser, Lang = paramList[0]
                if Path==sPath and re.search(HttpMethod, sHttpMethod) and re.search(Browser, sBrowser) and re.search(Lang, sLang):
                    registration = paramList[1]
                    self.__cache[(sPath, sHttpMethod, sBrowser, sLang)] = registration
                    return registration
            self.__cache[(sPath, sHttpMethod, sBrowser, sLang)] = None
            return None

class StoreConfiguration(object):
    def __init__(self):
        self.__config = []
        self.__cache = {}
        try:
            configXML = minidom.parse('conf/store.xml')
        except expat.ExpatError, v:
            raise serverExceptions.ConfigurationError, 'Error parsing store.xml (%s)' % v[0]
        regList = configXML.getElementsByTagName('reg')
        # construct action list
        for regNode in regList:
            sCC = regNode.getAttribute('cc')
            sMethod = regNode.getAttribute('method')
            sParam = regNode.getAttribute('param')
            sQS = regNode.getAttribute('qs') or ''
            sBrowser = regNode.getAttribute('client')
            sLang = regNode.getAttribute('lang')
            sAction = regNode.getAttribute('action')
            encoding = regNode.getAttribute('encoding').encode('iso-8859-1') or None
            max_age = regNode.getAttribute('max-age') or 0
            
            self.__config.append((
                 (sCC, sMethod, sParam, sQS, sBrowser, sLang),
                 Registration(sAction, encoding, getFiltersList(regNode), max_age)
            ))
            
        configXML.unlink()

    def getRegistration(self, sCC, sHttpMethod, sParam, sQS, sBrowser, sLang):
        if self.__cache.has_key((sCC, sHttpMethod, sParam, sQS, sBrowser, sLang)):
            return self.__cache[(sCC, sHttpMethod, sParam, sQS, sBrowser, sLang)]
        else:
            for paramList in self.__config:
                CC, HttpMethod, Param, QS, Browser, Lang = paramList[0]
                #print CC, HttpMethod, Param, Browser, Lang
                if re.search(CC, sCC) and re.search(HttpMethod, sHttpMethod) and \
                   Param == sParam and re.search(QS, sQS) and \
                   re.search(Browser, sBrowser) and re.search(Lang, sLang):
                    registration = paramList[1]
                    self.__cache[(sCC, sHttpMethod, sParam, sBrowser, sLang)] = registration
                    return registration
            self.__cache[(sCC, sHttpMethod, sParam, sBrowser, sLang)] = None
            return None

apps = {}

try:
    configDom = minidom.parse('conf/pubdir.xml')
except expat.ExpatError, v:
    raise serverExceptions.ConfigurationError, 'Error parsing apps.xml (%s)' % v[0]

for appNode in configDom.getElementsByTagName('dir'):
    webApp = App(appNode)
    apps[appNode.getAttribute('name')] = webApp

configDom.unlink()
del configDom

storeConfig = StoreConfiguration()