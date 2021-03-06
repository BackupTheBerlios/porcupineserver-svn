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
"Server configuration classes"

from xml.dom import minidom

class Locale(dict):
    def __getitem__(self, key):
        return self.get(key, key)

class ResourceStrings(object):
    def __init__(self, dctResources):
        self.__resources = dctResources

    def getResource(self, sName, sLocale):
        dctLocale = self.__resources.setdefault(sLocale, self.__resources['*'])
        return dctLocale[sName]
        
    def getLocale(self, sLocale):
        return self.__resources.setdefault(sLocale, self.__resources['*'])

dctResources = {}
resDom = minidom.parse('conf/stringresources.xml') 
for local in resDom.getElementsByTagName('locale'):
    sLang = local.getAttribute('lang')
    if not(dctResources.has_key(sLang)):
        dctResources[sLang] = Locale()
    localeResources = local.getElementsByTagName('res')
    for resource in localeResources:
        sType = ''
        if resource.hasAttribute('type'):
            sType = resource.getAttribute('type')
        if not sType:
            dctResources[sLang][resource.getAttribute('id')] = resource.childNodes[0].data.encode('utf-8')
        elif sType == 'array':
            dctResources[sLang][resource.getAttribute('id')] = resource.childNodes[0].data.encode('utf-8').split(';')
        
resDom.unlink()
stringResources = ResourceStrings(dctResources)
