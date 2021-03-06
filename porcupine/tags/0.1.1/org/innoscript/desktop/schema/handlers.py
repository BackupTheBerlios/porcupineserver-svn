#===============================================================================
#    Copyright 2005-2007, Tassos Koutsovassilis
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
"Porcupine desktop objects' event handlers"

from porcupine import serverExceptions
from porcupine.core import eventHandlers
from org.innoscript.desktop.schema import common

class PersonalFolderHandler(eventHandlers.ContentclassEventHandler):
    @classmethod
    def on_create(self, user, trans):
        if not user.personalFolder.value:
            # create user's personal folder
            personal_folder = common.PersonalFolder()
            user.personalFolder.value = personal_folder.id
            personal_folder.displayName.value = user.displayName.value
            
            # set security
            personal_folder.inheritRoles = False
            personal_folder.security = {
                'administrators' : 8,
                user.id : 2
            }
                        
            personal_folder.appendTo('personal', trans)
            
    @classmethod
    def on_update(self, user, old_user, trans):
        new_name = user.displayName.value
        old_name = old_user.displayName.value
        if new_name != old_name:
            personal_folder = user.personalFolder.getItem(trans)
            personal_folder.displayName.value = new_name
            personal_folder.update(trans)
    
    @classmethod
    def on_delete(self, user, trans, bPermanent):
        if bPermanent:
            personal_folder = user.personalFolder.getItem(trans)
            personal_folder.delete(trans)
