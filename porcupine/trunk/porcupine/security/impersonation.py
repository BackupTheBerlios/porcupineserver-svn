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
"User impersonation classess"

import types

from porcupine.db import db

def runas(userid):
    """
    The runas descriptor allows servlet methods to run under
    a specific user account.
    """
    class RunAs(object):
        def __init__(self, function):
            self.func = function
            self.name = function.func_name
            self.__doc__ = function.func_doc
            
        def __get__(self, servlet, servlet_class):
            def runas_wrapper(*args):
                user = db.getItem(userid)
                originalUser = servlet.session.user
                servlet.session.user = user
                try:
                    return self.func(*args)
                finally:
                    # restore original user unless
                    # the servlet hasn't switched identity
                    if servlet.session.user == user:
                        servlet.session.user = originalUser

            runas_wrapper.func_name = self.func.func_name
            return types.MethodType(runas_wrapper, servlet, servlet_class)
    
    return RunAs
