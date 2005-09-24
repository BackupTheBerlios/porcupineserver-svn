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
"""
Server proxy class module

@var proxy: This is assigned to the L{server<porcupine.core.servlet.BaseServlet.server>}
    attribute of each servlet.
@type proxy: L{Server}
"""
from porcupineserver import __version__
from porcupine.config import resources, serverSettings
from porcupine.db import dbEnv

class Server(object):
    """
    Porcupine Server proxy
    
    A single instance of this type is available during servlet execution.
    
    @type store: L{dbEnv<porcupine.db.dbEnv>}
    @type resources: L{ResourceStrings<porcupine.config.resources.ResourceStrings>}
    @type temp_folder: str
    @type version: str
    """
    def __init__(self):
        self.__dbenv = dbEnv
        self.__stringResources = resources.stringResources
        self.__tmpfldr = serverSettings.temp_folder

    def getTempFolder(self):
        """Getter of the L{temp_folder} property.
        
        @rtype: str
        """
        return self.__tmpfldr
    temp_folder = property(getTempFolder, None, None,
        'The server\'s temporary folder')

    def getStore(self):
        """Getter of the L{store} property.
        
        @rtype: L{dbEnv<porcupine.db.dbEnv>}
        """
        return self.__dbenv
    store = property(getStore, None, None, 'Porcupine database handle')

    def getResources(self):
        """Getter of the L{resources} property.
        
        @rtype: L{ResourceStrings<porcupine.config.resources.ResourceStrings>}
        """
        return self.__stringResources
    resources = property(getResources, None, None, 'Localization resources')
    
    def getVersion(self):
        """Getter of the L{version} property.
        
        @rtype: str
        """
        return __version__
    version = property(getVersion, None, None, 'The server\'s version')

proxy = Server()