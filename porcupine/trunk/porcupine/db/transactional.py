#===============================================================================
#    Copyright 2005-2008 Tassos Koutsovassilis
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
"The Porcupine transactional method descriptor."

import types

from porcupine import exceptions

class transactional(object):
    """
    This is the descriptor class of a Porcupine object's
    transactional method.
    
    It just records the corresponding method call
    to the transaction's actions, so that the transaction
    can be re-played in case of failure. This is triggered
    from here.
    """
    def __init__(self, function):
        self.func = function
        self.name = function.func_name
        self.__doc__ = function.func_doc
        
    def __get__(self, item, item_class):
        def transactional_wrapper(*args):
            # the transaction handle should always be the last argument
            trans = args[-1]
            trans.actions.append( (self.func, args) )
            return self.func(*args)
        transactional_wrapper.func_name = self.func.func_name
        return types.MethodType(transactional_wrapper, item, item_class)

