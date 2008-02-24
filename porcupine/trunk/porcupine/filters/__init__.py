#===============================================================================
#    Copyright 2005-2008, Tassos Koutsovassilis
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
Porcupine post and pre processing filters.
"""
from porcupine.db import db
from porcupine.core.decorators import WebMethodWrapper

from porcupine.filters import output
from porcupine.filters import authorization

def filter(filter_class, **kwargs):
    "filter decorator"
    class FDecorator(WebMethodWrapper):
        def get_wrapper(self):
            def f_wrapper(item, context):
                if (filter_class.type=='pre'):
                    filter_class.apply(context, None, **kwargs)
                self.decorator.__get__(item, item.__class__)(context)
                if (filter_class.type=='post'):
                    filter_class.apply(context, None, **kwargs)
            return f_wrapper
    return FDecorator

def runas(userid):
    """
    The runas filter allows web methods to run under
    a specific user account.
    """
    class RunAs(WebMethodWrapper):
        def get_wrapper(self):
            def runas_wrapper(item, context):
                user = db.getItem(userid)
                context.original_user = context.session.user
                context.session.user = user
                try:
                    self.decorator.__get__(item, item.__class__)(context)
                finally:
                    # restore original user unless
                    # the identity is not switched
                    if context.session.user == user:
                        context.session.user = context.original_user
            return runas_wrapper
    return RunAs

def i18n(resources):
    return filter(output.I18n, using=resources)

def gzip():
    return filter(output.Gzip)

def requires_login(redirect=None):
    return filter(authorization.RequiresLogin, redirect=redirect)

def requires_policy(policyid):
    return filter(authorization.RequiresPolicy, policyid=policyid)
