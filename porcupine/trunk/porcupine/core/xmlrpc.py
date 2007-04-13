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
"Porcupine XML-RPC Library"

import cStringIO
from porcupine.utils import date, xmlUtils
from porcupine.oql import core
from porcupine.core import objectSet
from porcupine import systemObjects, datatypes
from xml.dom import minidom

DEFAULT_PROPS = ('id', 'modified', 'owner', 'created', '__image__',
                 'contentclass', 'parentid', 'isCollection')

class XMLRPCParams(list):
    def __init__(self, oList=[], encoding='utf-8'):
        list.__init__(self, oList)
        self.method = None
        self.encoding = encoding

    def serialize(self):
        xml = cStringIO.StringIO()
        xml.write('<params>')
        for param in self:
            xml.write('<param>')
            xml.write(self.__serializeParam(param))
            xml.write('</param>')
        xml.write('</params>')
        sXml = xml.getvalue()
        xml.close()
        return(sXml)

    def loadXML(self, s):
        oDom = minidom.parseString(s)
        oMethodCall = oDom.getElementsByTagName('methodCall')[0]
        self.method = oMethodCall.getElementsByTagName('methodName')[0].childNodes[0].data
        params = oMethodCall.getElementsByTagName('params')
        if params:
            params = params[0].getElementsByTagName('param')
            for param in params:
                self.append(self.__getParam(param.getElementsByTagName('value')[0]))
        oDom.unlink()
        
    def __getParam(self, param):
        childNodes = self.__getDirectChildren(param)
        if len(childNodes)==1:
            param = childNodes[0]
            if param.tagName == 'string':
                if param.childNodes:
                    return(param.childNodes[0].data.encode(self.encoding))
                else:
                    return ''
            elif param.tagName == 'i4' or param.tagName == 'int':
                return(int(param.childNodes[0].data))
            elif param.tagName == 'boolean':
                return(bool(int(param.childNodes[0].data)))
            elif param.tagName == 'double':
                return(float(param.childNodes[0].data))
            elif param.tagName == 'dateTime.iso8601':
                oDate = date.Date.fromIso8601(param.childNodes[0].data)
                return(oDate)
            elif param.tagName == 'array':
                arr = []
                elements = self.__getDirectChildren(param.getElementsByTagName('data')[0])
                for element in elements:
                    arr.append(self.__getParam(element))
                return arr
            elif param.tagName == 'struct':
                struct = {}
                members = self.__getDirectChildren(param)
                for member in members:
                    sName = member.getElementsByTagName('name')[0].childNodes[0].data
                    memberValue = self.__getParam(member.getElementsByTagName('value')[0])
                    struct[sName] = memberValue
                return struct
        elif len(childNodes)==0:
            return(param.childNodes[0].data)

    def __getDirectChildren(self, node):
        children = [e for e in node.childNodes
                   if e.nodeType == e.ELEMENT_NODE]   
        return children

    def __serializeParam(self, param):
        if type(param)==str:
            return('<value>%s</value>' % xmlUtils.XMLEncode(param))
        elif type(param)==unicode:
            return('<value>%s</value>' % xmlUtils.XMLEncode(param.encode(self.encoding)))
        elif type(param)==int or type(param)==long:
            return('<value><i4>%i</i4></value>' % param)
        elif type(param)==bool:
            return('<value><boolean>%i</boolean></value>' % param)
        elif type(param)==float:
            return('<value><double>%f</double></value>' % param)
        elif type(param)==list or type(param)==tuple:
            sArray = '<value><array><data>'
            for elem in param:
                serialized = self.__serializeParam(elem)
                if serialized:
                    sArray += serialized
            sArray += '</data></array></value>'
            return(sArray)
        elif type(param)==dict:
            sStruct = '<value><struct>'
            for member in param.keys():
                serialized = self.__serializeParam(param[member])
                if serialized:
                    sStruct += '<member><name>%s</name>%s</member>' % \
                    (member, serialized)
            sStruct += '</struct></value>'
            return(sStruct)
        elif isinstance(param, objectSet.ObjectSet):
            sArray = '<value><array><data>'
            for rec in param:
                sArray += self.__serializeParam(rec)
            sArray += '</data></array></value>'
            return sArray
        elif isinstance(param, systemObjects.GenericItem):
            xmlrpc_object = {}
            for attr in param.__props__ + DEFAULT_PROPS:
                try:
                    oAttr = getattr(param, attr)
                except AttributeError:
                    continue
                if isinstance(oAttr, datatypes.ExternalAttribute):
                    xmlrpc_object[attr] = '[EXTERNAL STREAM]'
                else:
                    oAttr = core.getAttribute(param, [attr])
                    if isinstance(oAttr, objectSet.ObjectSet):
                        # we have an object set with objects
                        xmlrpc_object[attr] = [
                            {'id': x._id, 'displayName': x.displayName.value}
                            for x in oAttr
                        ]
                    else:
                        xmlrpc_object[attr] = oAttr
            return self.__serializeParam( xmlrpc_object )
        elif isinstance(param, date.Date):
            return '<value><dateTime.iso8601>%s</dateTime.iso8601></value>' % \
            param.toIso8601()
        else:
            return None#self.__serializeParam(str(param))
