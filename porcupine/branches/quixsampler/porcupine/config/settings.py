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
"Parser for ini file settings"

import ConfigParser

class Settings(object):
    def __init__(self):
        self.__options = []
    
    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name!='_Settings__options':
            self.__options.append(name)
    
    def setdefault(self, name, value):
        if hasattr(self, name):
            return(getattr(self, name))
        else:
            object.__setattr__(self, name, value)
            return(value)
    
    def toDict(self):
        d = {}
        for opt in self.__options:
            d[opt] = getattr(self, opt)
        return d
    
    def getOpt(self):
        return(self.__options)
    options = property(getOpt)

config = ConfigParser.RawConfigParser()
config.readfp(open('conf/porcupine.ini'))

settings = Settings()

for section in config.sections():
    setattr(settings, section, Settings())
    for setting in config.options(section):
        try:
            setattr(getattr(settings, section), setting, config.getint(section, setting))
        except ValueError:
            setattr(getattr(settings, section), setting, config.get(section, setting))

del config