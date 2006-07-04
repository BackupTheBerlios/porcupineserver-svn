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
"Porcupine server event handlers base classes"

class DatatypeEventHandler(object):
    def on_create(item, attr, trans):
        pass
    on_create = staticmethod(on_create)

    def on_update(item, new_attr, old_attr, trans):
        pass
    on_update = staticmethod(on_update)
    
    def on_delete(item, attr, trans, bPermanent):
        pass
    on_delete = staticmethod(on_delete)
    
